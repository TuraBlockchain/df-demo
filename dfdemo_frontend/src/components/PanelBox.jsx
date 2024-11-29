import { twMerge } from "tailwind-merge";
const PanelBox = ({ title, children, className }) => {
  return (
    <div
      className={twMerge(
        "max-w-[909px]  md:px-[86px] py-[30px] md:py-[76px] md:bg-[#424242] rounded-[20px]",
        className
      )}
    >
      <div className="pb-[40px] text-txtgreen text-[24px] md:text-5xl text-center">
        {title}
      </div>
      {children}
    </div>
  );
};

export default PanelBox;
