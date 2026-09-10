import { forwardRef } from "react";

const PromptInput = forwardRef(function PromptInput(
  { value, onChange, onKeyDown },
  ref,
) {
  return (
    <textarea
      ref={ref}
      value={value}
      onChange={onChange}
      onKeyDown={onKeyDown}
      placeholder="Work on anything"
      aria-label="Chat message"
      className="h-33 w-full resize-none border-0 bg-transparent px-7 py-6 text-xl leading-relaxed text-neutral-900 outline-none placeholder:text-neutral-400 sm:text-2xl"
    />
  );
});

export default PromptInput;