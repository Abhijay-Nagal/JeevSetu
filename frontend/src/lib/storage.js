import { api } from "./api";

export const MAX_IMAGE_BYTES = 5 * 1024 * 1024;

// The server rejects an oversized or non-image upload with an opaque error, and
// by then the user has already waited for the transfer -- check up front so
// the composer can say what is wrong straight away.
export function validateObservationImage(file) {
  if (!file) return null;
  if (!file.type.startsWith("image/")) return "That file isn't an image.";
  if (file.size > MAX_IMAGE_BYTES) {
    return `Image is too large (${(file.size / 1024 / 1024).toFixed(1)} MB). The limit is ${MAX_IMAGE_BYTES / 1024 / 1024} MB.`;
  }
  return null;
}

export async function uploadObservationImage(file) {
  const problem = validateObservationImage(file);
  if (problem) throw new Error(problem);

  const { url } = await api.uploadImage(file);
  return url;
}
