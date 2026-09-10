import { Mic, Plus } from "lucide-react";
import IconButton from "../../atoms/IconButton/IconButton";
import ModelSelect from "../../atoms/Select/Select";
import Clients from "../../Data/Client";
import SendButton from "../../atoms/Button/Button";
import Models from "../../Data/Model";

export default function ToolComposer({
  message,
  model,
  client,
  onClientChange,
  onModelChange,
  onSend,
}) {
  return (
    <div className="flex items-center justify-between px-5 pb-3">
      <IconButton
        icon={Plus}
        label="Add attachment"
        onClick={() => console.log("Open file chooser")}
      />

      <div className="flex items-center gap-2 sm:gap-4">
         {/* Client dropdown */}
        <ModelSelect
          value={client}
          onChange={onClientChange}
          options={Clients}
          ariaLabel="Choose client"
        />
        <ModelSelect
          value={model}
          onChange={onModelChange}
          options={Models}
        />

        <IconButton
          icon={Mic}
          label="Start voice input"
          onClick={() => console.log("Start microphone")}
        />

        <SendButton
          disabled={!message.trim()}
          onClick={onSend}
        />
      </div>
    </div>
  );
}