export default function SelectButton({
  value,
  onChange,
  options = [],
  ariaLabel = "Select option",
  className = "",
}) {
  return (
    <div className="relative">
      <select
        value={value}
        onChange={onChange}
        aria-label={ariaLabel}
        className={`max-w-44 cursor-pointer appearance-none bg-transparent py-2 pr-7 text-base text-neutral-900 outline-none sm:max-w-none sm:text-xl ${className}`}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

      <span className="pointer-events-none absolute right-1 top-1/2 -translate-y-1/2 text-xl text-neutral-400">
        ⌄
      </span>
    </div>
  );
}