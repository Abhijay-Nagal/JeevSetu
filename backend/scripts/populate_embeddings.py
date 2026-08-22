import os
import json
from google import genai
from supabase import create_client

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not api_key or not supabase_url or not supabase_key:
        print("Missing required environment variables (GEMINI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)")
        return

    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
    supabase = create_client(supabase_url, supabase_key)

    # Fetch chunks that don't have embeddings yet
    print("Fetching chunks without embeddings...")
    response = supabase.table("document_chunks").select("id, content").is_("embedding", "null").execute()
    chunks = response.data

    if not chunks:
        print("All chunks have embeddings!")
        return

    print(f"Found {len(chunks)} chunks to embed.")

    # Process in small batches
    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        contents = [c["content"] for c in batch]
        ids = [c["id"] for c in batch]

        print(f"Embedding batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}...")
        
        try:
            embed_res = client.models.embed_content(
                model='gemini-embedding-2',
                contents=contents,
            )
            
            # Update Supabase
            for idx, embedding_obj in enumerate(embed_res.embeddings):
                supabase.table("document_chunks").update({
                    "embedding": embedding_obj.values
                }).eq("id", ids[idx]).execute()
                
        except Exception as e:
            print(f"Error on batch starting at index {i}: {e}")

    print("Finished populating embeddings!")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
