const http = require("http");

const server = http.createServer((req, res) => {
    res.writeHead(200, { "Content-Type": "text/plain" });
    res.end("SERVER OK");
});

server.listen(5000, "0.0.0.0", () => {
    console.log("🔥 LISTENING ON 5000");
    console.log("ADDRESS:", server.address());
});