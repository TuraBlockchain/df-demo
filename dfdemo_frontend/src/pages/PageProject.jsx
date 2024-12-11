import { useState, useEffect } from "react";
import { SigningStargateClient } from "@cosmjs/stargate";
import PanelBox from "../components/PanelBox";
import {
  axiosInstance,
  endpoint_rpc,
  turaChainId,
} from "../config/config";
import {
  Dialog,
  DialogTrigger,
  DialogSurface,
  DialogTitle,
  DialogBody,
  DialogActions,
  DialogContent,
} from "@fluentui/react-dialog";
import { ToastContainer, toast } from "react-toastify";

const ModalChain = ({ children, chain }) => {
  const [nftAddress, setNftAddress] = useState("");
  const [mintAddress, setMintAddress] = useState("");
  const [walletAddress, setWalletAddress] = useState(null);

  const [json, setJson] = useState();
  const [jsonStr, setJsonStr] = useState();
  const [intro, setIntro] = useState();
  const [keplrLoaded, setKeplrLoaded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const loadKeplr = async () => {
      if (window.keplr) {
        await window.keplr.enable(turaChainId); // 替换为你的链 ID
        setKeplrLoaded(true);
      } else {
        toast.error("Please install the Keplr plug-in");
      }
    };
    loadKeplr();
  });

  useEffect(() => {
    const address = localStorage.getItem("tura_address");
    setWalletAddress(address);
  }, []);

  const handleConnectWallet = async () => {
    try {

      // 连接 Keplr 钱包
      if (!window.keplr) {
        alert("Please install Keplr extension");
        return;
      }
      setIsLoading(true)
      const chainId = turaChainId;
      // 提示 Keplr 连接
      await window.keplr.enable(chainId);
      // 获取离线签名者
      const offlineSigner = window.getOfflineSigner(chainId);
      const accounts = await offlineSigner.getAccounts();
      // 假设新的地址是 accounts[0].address
      const newAddress = accounts[0].address;
      localStorage.setItem("tura_address", newAddress);
      setWalletAddress(newAddress);
      setIsLoading(false);

    } catch (error) {
      console.error("Failed to connect to Keplr", error);
      setIsLoading(false);
      alert("Failed to connect to Keplr");
    }
  }

  const handleSubmitClick = async (event) => {
    event.preventDefault();
    if (!keplrLoaded) {
      toast.error("Keplr is not loaded");
      return;
    }

    try {
      const chainId = turaChainId; // 替换为你的链 ID
      const address = localStorage.getItem("tura_address");
      if (!address) {
        toast.error("Please connect wallet");
        return;
      }

      const toAddress = address;
      const denom = "utura";
      const toSend = "1000000"; // 最小交易金额

      const offlineSigner = window.getOfflineSigner(chainId);
      const signingClient = await SigningStargateClient.connectWithSigner(
        endpoint_rpc, // 替换为你的节点 RPC URL
        offlineSigner
      );

      const fee = {
        amount: [{ denom: "utura", amount: "500" }], // 调整为你的交易费用
        gas: "200000",
      };

      const memo = jsonStr;
      toast.info("Loading...", {
        position: "top-right", // 设置位置为右上角
        autoClose: false,
        hideProgressBar: true,
        closeOnClick: false,
        pauseOnHover: false,
        draggable: false,
        progress: undefined,
        theme: "colored",
        type: "info",
        icon: false,
        toastId: "customId",
      });
      setIsLoading(true)
      const result = await signingClient.sendTokens(
        address,
        toAddress,
        [
          {
            denom: denom,
            amount: toSend,
          },
        ],
        fee,
        memo
      );
      toast.dismiss();

      toast.success(`Transaction Successfully`);
      fetchCreateData();

      // navigate("/some-path");
    } catch (error) {
      if (error.message === "Invalid string. Length must be a multiple of 4") {
        toast.dismiss();
        toast.success(`Transaction Successfully`);
        fetchCreateData();
      } else {
        toast.error(`Submit Error: ${error.message}`);
      }
    }
  };

  const fetchNFTData = async () => {
    try {
      setIsLoading(true);
      toast.info("Loading...");
      const response = await axiosInstance.get("tagfusion/api/get_nft_data", {
        params: {
          walletAddress: nftAddress,
        },
      });
      console.log(response);
      if (response.data.code === 0) {
        const data = response.data.data;
        if (data) {
          setJson(data);
          setJsonStr(JSON.stringify(data));
        }
      } else {
        toast.error(response.data.message);
      }
      toast.dismiss();

      setIsLoading(false);
    } catch (e) {
      console.log(e);
      setIsLoading(false);
    }
  };

  const fetchCreateData = async () => {
    try {
      const address = localStorage.getItem("tura_address");
      if (!address) {
        return;
      }
      setIsLoading(true);
      const formData = new FormData();
      formData.append("tura_address", address);
      formData.append("json", jsonStr);
      formData.append("uuid", json["uuid"]);
      const response = await axiosInstance.post(
        "tagfusion/api/create_up_chain_data/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      console.log(response);
      if (response.data.code === 0) {
        setOpen(false);
      } else {
        toast.error(response.data.message);
      }
      setIsLoading(false);
    } catch (e) {
      console.log(e);
      setIsLoading(false);
    }
  };

  const fetchInfo = async () => {
    const id = chain.id;
    if (!id) {
      return;
    }
    try {
      setIsLoading(true);
      const response = await axiosInstance.get(
        `tagfusion/api/get_chain_introduction/`,
        {
          params: {
            id: id,
          },
        }
      );
      console.log(response);
      if (response.data.code === 0) {
        const result = response.data.data;
        const info = result.Introduction;
        setIntro(info);
      } else {
        toast.error(response.data.message);
      }
      setIsLoading(false);
    } catch (e) {
      console.log(e);
      setIsLoading(false);
    }
  };

  const handleConfirmClick = () => {
    if (!nftAddress || isLoading) {
      toast.error("Please enter address");

      return;
    }
    fetchNFTData();
  };

  const handleOpenDialog = (event, data) => {
    setOpen(data.open);
    if (data.open) {
      fetchInfo();
    } else {
      setJson();
      setJsonStr("");
      setIntro("");
    }
  };

  const handleAddressChange = (e) => {
    let val = e.target.value;
    setNftAddress(val);
  };
  const handleMintAddressChange = (e) => {
    let val = e.target.value;
    setMintAddress(val);
  };
  return (
    <Dialog open={open} onOpenChange={handleOpenDialog}>
      <DialogTrigger disableButtonEnhancement>{children}</DialogTrigger>
      <DialogSurface style={{ maxWidth: "fit-content" }}>
        <DialogBody>
          <DialogContent>
            <div className="max-w-[1200px]">
              <div className="origin-top">
                <div className="flex justify-center items-center">
                  <div className="relative flex-none flex flex-col items-center  w-[85%] md:w-[596px] px-[20px] md:px-[56px] py-[20px] md:py-[48px]  rounded-[10px] bg-[#424242]">
                    <div className="max-h-[200px] min-w-[260px] overflow-auto mt-[32px] text-[14px] text-white text-left whitespace-pre-line">
                      <p>{intro?.replaceAll("\\n", "\n")}</p>
                    </div>
                    <div className="w-full">
                      <div className="relative mt-[20px]">
                        <input
                          onChange={handleAddressChange}
                          value={nftAddress}
                          type="text"
                          placeholder="Wallet Address"
                          className="w-full px-[10px] py-[10px] border border-[#FFFFFF1F] text-[#FFFFFF8A] text-[16px] bg-[#FFFFFF1A] outline-none focus:border-b-[#FFA000FF]"
                        />
                      </div>
                      <div className="flex flex-col md:flex-row gap-[8px]">
                        <div
                          onClick={handleConfirmClick}
                          className={`flex justify-center items-center h-[40px] mt-[20px] px-[15px] bg-btngreen text-white cursor-pointer ${
                            !nftAddress || isLoading ? "opacity-50" : ""
                          }`}
                        >
                          Confirm
                        </div>

                        <div
                          className={`flex justify-center items-center h-[40px] mt-[20px] px-[15px] bg-btngreen text-white cursor-pointer`}
                        >
                          <a
                            href="https://faucet.tagfusion.org/"
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            Get Tura fee here
                          </a>
                        </div>
                      </div>
                      <div className="w-full h-[150px] mt-[20px] p-[8px] border border-[#FFA000FF] text-[14px] text-white text-left overflow-auto text-wrap whitespace-pre break-words">
                        {jsonStr}
                      </div>
                      <div className="flex justify-center">
                        {walletAddress ? (
                          <div
                            onClick={handleSubmitClick}
                            className={`flex justify-center items-center h-[40px] mt-[20px] px-[15px] bg-btngreen text-white cursor-pointer ${
                              isLoading || !jsonStr ? "opacity-50" : ""
                            }`}
                          >
                            Submit
                          </div>
                        ) : (
                          <div
                            onClick={handleConnectWallet}
                            className={`flex justify-center items-center h-[40px] mt-[20px] px-[15px] bg-btngreen text-white cursor-pointer ${
                              isLoading ? "opacity-50" : ""
                            }`}
                          >
                            Connect Wallet
                          </div>
                        )}
                        
                        <div
                          onClick={() => {
                            setOpen(false);
                          }}
                          className={`flex justify-center items-center h-[40px] mt-[20px] ml-[8px] px-[15px] bg-btngreen text-white cursor-pointer `}
                        >
                          close
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </DialogContent>
          <DialogActions>
            <DialogTrigger disableButtonEnhancement>
              {/* <Button appearance="secondary">Close</Button> */}
            </DialogTrigger>
            {/* <Button appearance="primary">Do Something</Button> */}
          </DialogActions>
        </DialogBody>
      </DialogSurface>
    </Dialog>
  );
};

const PageProject = () => {
  const tags = [
    {
      tag_name: "Solana",
      id: 1,
      status: "ready"
    }, 
    {
      tag_name: "Ethereum",
      id: 2,
      status: ""
    }, 
    {
      tag_name: "Polygan",
      id: 3,
      status: ""
    }, 
    {
      tag_name: "Immutable X",
      id: 4,
      status: ""
    }, 
    {
      tag_name: "BSC",
      id: 5,
      status: ""
    }, 
  ];

  return (
    <div className="flex justify-center pt-[140px]">
      <PanelBox
        title=""
        className="min-w-[300px] max-w-[1200px] bg-[#424242] mt-[30px]"
      >
        <div className="min-h-[150px] md:min-h-[500px]">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-[50px] gap-y-[30px] text-white">
            {tags.map((tag, index) =>
              tag.status === "ready" ? (
                <ModalChain key={index} chain={tag}>
                  <div
                    key={index}
                    className={`inline-flex justify-center items-center min-w-[200px] min-h-[40px] mx-[20px] md:mx-0 border rounded-[8px] cursor-pointer hover:border-[#FFA000FF] hover:text-[#FF6F00] transition-all`}
                  >
                    {tag.tag_name}
                  </div>
                </ModalChain>
              ) : (
                <div
                  key={index}
                  className={`inline-flex justify-center items-center min-w-[200px] min-h-[40px] mx-[20px] md:mx-0 px-[5px] border rounded-[8px] cursor-pointer hover:border-[#FFA000FF] hover:text-[#FF6F00] transition-all`}
                >
                  {tag.tag_name} (In Preparation)
                </div>
              )
            )}
          </div>
          <ModalChain></ModalChain>
        </div>
      </PanelBox>
      {/* <ToastContainer /> */}
    </div>
  );
};

export default PageProject;
