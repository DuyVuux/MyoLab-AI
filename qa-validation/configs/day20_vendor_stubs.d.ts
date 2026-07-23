declare namespace JSX {
  type Element = unknown;
  interface ElementChildrenAttribute { children: unknown; }
  interface IntrinsicAttributes { key?: string | number; }
  interface IntrinsicElements { [elementName: string]: unknown; }
}

declare module "react" {
  export type ReactNode = unknown;
  export function useState<T>(initial: T): [T, (value: T | ((previous: T) => T)) => void];
  export function useEffect(effect: () => void | (() => void), dependencies: readonly unknown[]): void;
  export function lazy<T>(loader: () => Promise<{ default: T }>): T;
  export const Suspense: (props: { children: ReactNode; fallback: ReactNode }) => JSX.Element;
}

declare module "react-router-dom" {
  import type { ReactNode } from "react";
  export const BrowserRouter: (props: { children: ReactNode }) => JSX.Element;
  export const Routes: (props: { children: ReactNode }) => JSX.Element;
  export const Route: (props: { path: string; element: ReactNode }) => JSX.Element;
  export const Navigate: (props: { to: string; replace?: boolean }) => JSX.Element;
  export const Link: (props: { to: string; className?: string; children: ReactNode }) => JSX.Element;
  export const NavLink: (props: { to: string; className?: string | ((state: { isActive: boolean }) => string); children: ReactNode }) => JSX.Element;
}

declare module "lucide-react" {
  interface IconProps { readonly size?: number; readonly [key: string]: unknown; }
  export const Activity: (props: IconProps) => JSX.Element;
  export const ClipboardList: (props: IconProps) => JSX.Element;
  export const FlaskConical: (props: IconProps) => JSX.Element;
  export const LayoutDashboard: (props: IconProps) => JSX.Element;
  export const MessageSquare: (props: IconProps) => JSX.Element;
}
