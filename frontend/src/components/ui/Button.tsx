import type { ButtonHTMLAttributes, ReactNode } from "react";

const baseStyles =
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400 disabled:cursor-not-allowed disabled:opacity-60";

const variantStyles: Record<string, string> = {
  primary: "bg-slate-900 text-white hover:bg-slate-800",
  secondary: "bg-slate-100 text-slate-900 hover:bg-slate-200",
  danger: "bg-red-600 text-white hover:bg-red-500",
  ghost: "bg-transparent text-slate-700 hover:bg-slate-100",
};

const sizeStyles: Record<string, string> = {
  sm: "px-3 py-1.5",
  md: "px-4 py-2",
  lg: "px-5 py-2.5",
};

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
};

export function Button({
  className,
  variant = "primary",
  size = "md",
  isLoading = false,
  leftIcon,
  rightIcon,
  children,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className ?? ""}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {leftIcon ? <span className="mr-2 inline-flex">{leftIcon}</span> : null}
      {isLoading ? "Chargement..." : children}
      {rightIcon ? <span className="ml-2 inline-flex">{rightIcon}</span> : null}
    </button>
  );
}
