import { supabase } from "./supabaseClient";

export const MAX_IMAGE_BYTES = 5 * 1024 * 1024;

// Supabase rejects an oversized or non-image upload with an opaque error, and
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

  // A file dropped in from a camera roll can arrive without an extension;
  // fall back to the MIME subtype so the stored object stays readable.
  const nameExtension = file.name.includes(".") ? file.name.split(".").pop().toLowerCase() : "";
  const extension = nameExtension || file.type.split("/")[1] || "jpg";
  const path = `${crypto.randomUUID()}.${extension}`;

  const { error } = await supabase.storage.from("observation-images").upload(path, file);
  if (error) throw error;

  const { data } = supabase.storage.from("observation-images").getPublicUrl(path);
  return data.publicUrl;
}
