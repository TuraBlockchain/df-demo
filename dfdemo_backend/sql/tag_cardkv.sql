-- 创建表结构
CREATE TABLE IF NOT EXISTS tags_cardkv (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    data JSONB NOT NULL
);

-- 插入数据
INSERT INTO tags_cardkv (id, name, data) VALUES
(1, 'CEX Trader', '{"CEX Trader": ["Binance", "Coinbase", "OKx", "Bybit", "Upbit", "Kraken", "Gate.io", "HTX", "Bitfinex", "Kucoin", "MEXC", "Bitget", "Crypto.com Exchange", "BingX", "Bitstamp", "Lbank", "Bitmart", "Bithumb", "Gemini", "Tokocrypto"]}'),
(2, 'Crypto Holer', '{"Crypto Holer": ["Dogs", "BTC", "ETH", "USDT", "BNB", "SOL", "USDC", "XRP", "TON", "DOGE", "ADA", "TRX", "AVAX", "SHIB", "DOT", "LINK", "BCH", "NEAR", "DAI", "LTC", "MATIC", "UNI", "PEPE", "APT", "ATOM", "RNDR", "OKB", "SUI", "INJ", "NOT", "ONDO"]}'),
(3, 'Dao Member', '{"Dao Member": ["Tagger Dao", "Bodong Dao"]}');
