import { supabase } from "./supabaseClient";

export async function uploadObservationImage(file) {
  const extension = file.name.split(".").pop();
  const path = `${crypto.randomUUID()}.${extension}`;

  const { error } = await supabase.storage.from("observation-images").upload(path, file);
  if (error) throw error;

  const { data } = supabase.storage.from("observation-images").getPublicUrl(path);
  return data.publicUrl;
}
