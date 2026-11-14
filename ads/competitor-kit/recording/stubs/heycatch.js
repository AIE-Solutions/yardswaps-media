import React from 'react';
const noop = () => {};
export const analytics = new Proxy({}, { get: () => noop });
export function HeyCatchProvider({ children }) { return React.createElement(React.Fragment, null, children); }
export default { analytics, HeyCatchProvider };
