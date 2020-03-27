const { createProxyMiddleware } = require('http-proxy-middleware');
module.exports = function(app) {
    app.use(
        ['/api', '/websocket', '/assets/public/keycard.jpeg'],
        createProxyMiddleware({
            target: "http://localhost:8888",
            ws: true
        })
    );
};
