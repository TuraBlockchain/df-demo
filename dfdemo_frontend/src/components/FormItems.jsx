const UploadCustom = ({onChange, uploadPic}) => {
  return (
    <div className="custom-upload relative ">
      <label>Upload Pic*</label>
      <div className="btn-select hidden items-center pt-[38px] pl-[6px] rounded-md focus:bg-black">
        <label
          htmlFor="uploadPic"
          className="px-[30px] py-[15px] text-[14px] leading-[17px] hover:text-white border border-[#79C077FF] cursor-pointer  hover:bg-[#FFFFFF09] "
        >
          Select
          <input
            type="file"
            id="uploadPic"
            className="hidden"
            onChange={onChange?.bind(this)}
          />
        </label>
      </div>
      <div className="absolute right-0 top-1/2 translate-y-[-50%] h-24 w-24 ml-[30px] rounded-lg flex items-center justify-center mr-4">
        {uploadPic && (
          <img
            src={URL.createObjectURL(uploadPic)}
            alt="Uploaded Pic"
            className="h-full w-full object-cover rounded-lg"
          />
        )}
      </div>
    </div>
  );
};

const InputCustom = ({ label, value, onChange, readonly }) => {
  return (
    <div className={`custom-ipt ${value ? "filled" : ""}`}>
      <input
        value={value}
        size="large"
        required
        readOnly={readonly}
        className=""
        onChange={onChange?.bind(this)}
      />
      <label>{label}</label>
    </div>
  );
};

const CheckBoxCustom = ({check, onChange}) => {
  return (
    <div className="custom-ckb">
      <input
        type="checkbox"
        value={check}
        checked={check}
        onChange={onChange?.bind(this)}
      />
    </div>
  );
};

export { InputCustom, UploadCustom, CheckBoxCustom };
