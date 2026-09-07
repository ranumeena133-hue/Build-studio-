const http = require('http');
const fs = require('fs');
const path = require('path');

// जिस folder को AI को access देना है, उसका path यहाँ डालें
const ROOT_DIR = '/data/data/com.termux/files/home/storage/shared/MyAIFolder';

// सर्वर बनाएँ
const server = http.createServer((req, res) => {
  res.setHeader('Content-Type', 'application/json');

  // सिर्फ POST requests मानें
  if (req.method !== 'POST') {
    res.writeHead(405).end(JSON.stringify({ error: 'Only POST allowed' }));
    return;
  }

  let body = '';
  req.on('data', chunk => body += chunk);
  req.on('end', () => {
    try {
      const rpc = JSON.parse(body);
      handleRPC(rpc, res);
    } catch (e) {
      res.end(JSON.stringify({ jsonrpc: '2.0', error: { code: -32700, message: 'Parse error' }, id: null }));
    }
  });
});

// RPC हैंडलर
function handleRPC(rpc, res) {
  const { method, params, id } = rpc;

  // FIX 2: notification (bina id) ka jawab nahi dena — warna MCP client confuse hota hai
  if (id === undefined) {
    res.writeHead(202).end();
    return;
  }

  // initialize
  if (method === 'initialize') {
    res.end(JSON.stringify({
      jsonrpc: '2.0',
      result: {
        protocolVersion: '2024-11-05',
        capabilities: { tools: {} },
        serverInfo: { name: 'mera-mcp-server', version: '1.0.0' }
      },
      id
    }));
    return;
  }

  // tools/list
  if (method === 'tools/list') {
    res.end(JSON.stringify({
      jsonrpc: '2.0',
      result: {
        tools: [
          {
            name: 'list_files',
            description: 'List all files in the folder',
            inputSchema: { type: 'object', properties: {} }
          },
          {
            name: 'read_file',
            description: 'Read content of a file',
            inputSchema: {
              type: 'object',
              properties: { path: { type: 'string' } },
              required: ['path']
            }
          },
          {
            name: 'write_file',
            description: 'Write or update a file',
            inputSchema: {
              type: 'object',
              properties: {
                path: { type: 'string' },
                content: { type: 'string' }
              },
              required: ['path', 'content']
            }
          },
          {
            name: 'delete_file',
            description: 'Delete a file',
            inputSchema: {
              type: 'object',
              properties: { path: { type: 'string' } },
              required: ['path']
            }
          }
        ]
      },
      id
    }));
    return;
  }

  // tools/call
  if (method === 'tools/call') {
    // FIX 4: params na aaye to server crash nahi hoga
    const { name, arguments: args } = params || {};
    let result;
    try {
      switch (name) {
        case 'list_files':
          const files = fs.readdirSync(ROOT_DIR);
          result = { content: [{ type: 'text', text: files.length ? files.join('\n') : '(folder empty)' }] };
          break;
        case 'read_file':
          const readPath = safeJoin(args.path);
          result = { content: [{ type: 'text', text: fs.readFileSync(readPath, 'utf8') }] };
          break;
        case 'write_file':
          const writePath = safeJoin(args.path);
          fs.mkdirSync(path.dirname(writePath), { recursive: true });
          fs.writeFileSync(writePath, args.content, 'utf8');
          result = { content: [{ type: 'text', text: 'File written: ' + args.path }] };
          break;
        case 'delete_file':
          const deletePath = safeJoin(args.path);
          fs.unlinkSync(deletePath);
          result = { content: [{ type: 'text', text: 'File deleted: ' + args.path }] };
          break;
        default:
          throw new Error('Unknown tool: ' + name);
      }
      res.end(JSON.stringify({ jsonrpc: '2.0', result, id }));
    } catch (e) {
      res.end(JSON.stringify({
        jsonrpc: '2.0',
        error: { code: -32603, message: e.message },
        id
      }));
    }
    return;
  }

  // unknown method
  res.end(JSON.stringify({
    jsonrpc: '2.0',
    error: { code: -32601, message: 'Method not found' },
    id
  }));
}

// FIX 1: Path traversal se PAKKA bachav (sibling-folder wali chaal bhi band)
function safeJoin(userPath) {
  const fullPath = path.resolve(ROOT_DIR, userPath);
  if (fullPath !== ROOT_DIR && !fullPath.startsWith(ROOT_DIR + path.sep)) {
    throw new Error('Invalid path');
  }
  return fullPath;
}

// सर्वर को port 3000 पर सुनाएँ
server.listen(3000, () => {
  console.log('MCP server running on http://localhost:3000');
});
