import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || "https://myulzfvwnxrxbqslfojh.supabase.co";
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || "sb_publishable_oIhMIkW9l0E0-XDGspMuNw_kS5BGuV5";

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
