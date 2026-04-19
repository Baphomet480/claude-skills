#!/usr/bin/env node
// Spawn Gemini CLI in ACP mode, send one prompt, stream response to stdout.
// Usage: node gemini-delegate.mjs <prompt text...>
// Env:   GEMINI_MODEL (default: gemini-2.5-pro)
//        GEMINI_CLI_VERSION (default: nightly)
//        TARGET_CWD (default: process.cwd())

import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { Readable, Writable } from 'node:stream';
import { ClientSideConnection, ndJsonStream } from '@agentclientprotocol/sdk';

const args = process.argv.slice(2);
if (!args.length) {
  process.stderr.write('Usage: node gemini-delegate.mjs <prompt text>\n');
  process.exit(1);
}

const promptText = args.join(' ');
const model = process.env.GEMINI_MODEL ?? 'gemini-2.5-pro';
const version = process.env.GEMINI_CLI_VERSION ?? 'nightly';
const cwd = process.env.TARGET_CWD ?? process.cwd();

const child = spawn(
  'pnpm',
  ['dlx', `@google/gemini-cli@${version}`, '--acp', '--yolo', '--model', model],
  {
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd,
    env: { ...process.env, TERM: 'dumb' },
    detached: true,
  },
);

child.on('error', (err) => {
  process.stderr.write(`[gemini-delegate] spawn error: ${err.message}\n`);
  process.exit(1);
});

if (child.stderr) {
  child.stderr.on('data', (data) => {
    const line = data.toString().trim();
    if (line) process.stderr.write(`[gemini] ${line}\n`);
  });
}

// stdin → writes TO the subprocess (our output stream)
// stdout → reads FROM the subprocess (our input stream)
const inStream = Writable.toWeb(child.stdin);
const outStream = Readable.toWeb(child.stdout);
const stream = ndJsonStream(inStream, outStream);

const connection = new ClientSideConnection(
  (_agent) => ({
    sessionUpdate: async (params) => {
      const upd = params?.update ?? params;
      if (upd?.sessionUpdate === 'agent_message_chunk') {
        // ACP puts the text at content.text; delta is a legacy/alternate field.
        const chunk = upd.delta ?? upd.content?.text ?? '';
        if (chunk) process.stdout.write(chunk);
      }
    },
    requestPermission: async (_params) => ({
      outcome: { outcome: 'cancelled' },
    }),
  }),
  stream,
);

await connection.initialize({ clientCapabilities: {}, protocolVersion: 1 });
const { sessionId } = await connection.newSession({ cwd, mcpServers: [] });

await connection.prompt({
  sessionId,
  messageId: randomUUID(),
  prompt: [{ type: 'text', text: promptText }],
});

process.stdout.write('\n');

try {
  if (child.pid) process.kill(-child.pid, 'SIGTERM');
} catch {
  child.kill('SIGTERM');
}

process.exit(0);
