#!/usr/bin/env node
// Spawn Claude Code ACP adapter, send one prompt, stream response to stdout.
// Usage: node claude-delegate.mjs <prompt text...>
// Env:   CLAUDE_MODEL (default: claude-sonnet-4-6)
//        TARGET_CWD (default: process.cwd())

import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { Readable, Writable } from 'node:stream';
import os from 'node:os';
import { ClientSideConnection, ndJsonStream } from '@agentclientprotocol/sdk';

const args = process.argv.slice(2);
if (!args.length) {
  process.stderr.write('Usage: node claude-delegate.mjs <prompt text>\n');
  process.exit(1);
}

const promptText = args.join(' ');
const model = process.env.CLAUDE_MODEL ?? 'claude-sonnet-4-6';
const cwd = process.env.TARGET_CWD ?? process.cwd();

const env = { ...process.env, TERM: 'dumb', CLAUDE_CODE_SKIP_PERMISSIONS: '1' };
// The adapter refuses to start inside another Claude Code session.
delete env.CLAUDECODE;
// Systemd / restricted PATH may omit ~/.local/bin where `claude` lives.
if (!env.CLAUDE_CODE_EXECUTABLE) {
  const localBin = `${os.homedir()}/.local/bin`;
  env.PATH = `${localBin}:${env.PATH ?? ''}`;
}

const child = spawn('pnpm', ['dlx', '@zed-industries/claude-code-acp'], {
  stdio: ['pipe', 'pipe', 'pipe'],
  cwd,
  env,
  detached: true,
});

child.on('error', (err) => {
  process.stderr.write(`[claude-delegate] spawn error: ${err.message}\n`);
  process.exit(1);
});

if (child.stderr) {
  child.stderr.on('data', (data) => {
    const line = data.toString().trim();
    if (line) process.stderr.write(`[claude] ${line}\n`);
  });
}

// stdin → writes TO the subprocess; stdout → reads FROM the subprocess
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

// Apply model — claude-code-acp has no CLI flag for this; must use ACP RPC.
if (model) {
  try {
    await connection.unstable_setSessionModel({ sessionId, modelId: model });
  } catch {
    // Not fatal — adapter may not support this yet.
  }
}

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
