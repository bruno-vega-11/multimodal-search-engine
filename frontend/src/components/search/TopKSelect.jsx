import Select from "../ui/Select";
import { TOP_K_OPTIONS } from "../../lib/constants";

export default function TopKSelect({ value, onChange, className }) {
  return <Select value={value} onChange={onChange} options={TOP_K_OPTIONS} className={className} />;
}
