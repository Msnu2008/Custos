# limpia_env.py
with open(".env", "r", encoding="utf-8") as file:
    lines = file.readlines()

with open(".env", "w", encoding="utf-8") as file:
    for line in lines:
        if "SUPABASE_URL" in line:
            file.write("SUPABASE_URL=https://rsufcgunjghffncclfsx.supabase.co\n")
        else:
            file.write(line)
