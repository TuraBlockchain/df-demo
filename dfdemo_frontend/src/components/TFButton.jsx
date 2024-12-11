import { useNavigate } from "react-router-dom";

const TFButton = ({
  className = "",
  onClick = () => {},
  to = "",
  link = "",
  children
}) => {
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
    onClick(e);
  };

  return (
    <button
      className={`px-[30px] py-[15px] text-white bg-btngreen  ${className}`}
      onClick={handleClick}
    >
      {children}
    </button>
  );
};

export default TFButton;
