declare namespace JSX{type Element=unknown;interface ElementChildrenAttribute{children:unknown;}interface IntrinsicAttributes{key?:string|number;}interface IntrinsicElements{[name:string]:unknown;}}
declare module'react-router-dom'{import type{ReactNode}from'react';export const Route:(props:{path:string;element:ReactNode})=>JSX.Element;}
declare module'react'{export type ReactNode=unknown;}
