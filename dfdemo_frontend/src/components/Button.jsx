import { useNavigate } from "react-router-dom";

const Button = ({ className = "", text = "", onClick = () => {}, to = "", link = "" }) => {
   const navigate = useNavigate();

   const handleClick = (e) => {
      if (link) {
         // If link is an external URL, open it in a new tab
         if (link.startsWith("http://") || link.startsWith("https://")) {
            window.open(link, "_blank", "noopener,noreferrer");
         } else {
            e.preventDefault();
            navigate(link);
         }
      } else if (to) {
         e.preventDefault();
         navigate("/", { replace: true });
         setTimeout(() => {
            document.getElementById(to)?.scrollIntoView({ behavior: "smooth" });
         }, 100); // Adding a small delay to ensure navigation is complete before scrolling
      }
      onClick();
   };

   return (
       <button
           className={`font-semibold border border-primary-default rounded-full min-w-[140px] h-[50px] capitalize flex items-center justify-center ${className}`}
           onClick={handleClick}
       >
          {text}
       </button>
   );
};

export default Button;
