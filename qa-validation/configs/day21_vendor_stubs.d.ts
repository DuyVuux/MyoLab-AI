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
  export function useRef<T>(initial: T): { current: T };
  export function useMemo<T>(factory: () => T, dependencies: readonly unknown[]): T;
}
declare module "react-router-dom" {
  import type { ReactNode } from "react";
  export const Route: (props: { path: string; element: ReactNode }) => JSX.Element;
}
