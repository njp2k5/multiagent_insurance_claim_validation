import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

/** Vite plugin that exposes POST /__log so the browser can send logs to this terminal */
function terminalLogPlugin(): Plugin {
  return {
    name: "terminal-log",
    configureServer(server) {
      server.middlewares.use("/__log", (req, res) => {
        if (req.method === "POST") {
          let body = "";
          req.on("data", (chunk: Buffer) => (body += chunk.toString()));
          req.on("end", () => {
            try {
              const { tag, args } = JSON.parse(body);
              console.log(`\x1b[36m[${tag}]\x1b[0m`, ...args);
            } catch {
              console.log(body);
            }
            res.writeHead(204);
            res.end();
          });
        } else {
          res.writeHead(204);
          res.end();
        }
      });
    },
  };
}

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "localhost",
    port: 5000,
    strictPort: true,
    hmr: {
      overlay: false,
    },
  },
  plugins: [react(), terminalLogPlugin(), mode === "development" && componentTagger()].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
