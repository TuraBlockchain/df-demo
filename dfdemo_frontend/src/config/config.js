// config.js
import axios from "axios";

const config = {
    endpoint: 'https://tagfusion.org/'
};


const endpoint_rpc = "https://rpc-beta1.turablockchain.com"

const axiosInstance = axios.create({
    baseURL: config.endpoint,
    timeout: 10000,  // 设置超时时间为 10000 毫秒（10 秒）
    headers: {
        'Content-Type': 'application/json',
        // 如果需要身份验证，可以添加 'Authorization': 'Bearer YOUR_TOKEN'
    } // 设置超时时间为 10000 毫秒（10 秒）

});

const turaChainId = "mainnet-tura";

export { axiosInstance, turaChainId, endpoint_rpc};
