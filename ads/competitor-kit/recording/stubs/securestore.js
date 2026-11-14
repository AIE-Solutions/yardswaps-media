export async function getItemAsync(k) { try { return localStorage.getItem(k); } catch { return null; } }
export async function setItemAsync(k, v) { try { localStorage.setItem(k, v); } catch {} }
export async function deleteItemAsync(k) { try { localStorage.removeItem(k); } catch {} }
export function getItem(k) { try { return localStorage.getItem(k); } catch { return null; } }
export function setItem(k, v) { try { localStorage.setItem(k, v); } catch {} }
export const isAvailableAsync = async () => true;
export const WHEN_UNLOCKED = 'WHEN_UNLOCKED';
export const AFTER_FIRST_UNLOCK = 'AFTER_FIRST_UNLOCK';
