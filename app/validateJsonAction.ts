"use server";
import { put } from "@vercel/blob"; // Generated by Copilot

// Generated by Copilot
export async function validateJson(message: string) {
  try {
    const parsed = JSON.parse(message); // Generated by Copilot

    // Generate a random filename
    const filename = `${crypto.randomUUID()}.json`; // Generated by Copilot

    // Upload the JSON to Vercel Blob Storage
    const blob = await put(filename, JSON.stringify(parsed, null, 2), {
      contentType: "application/json",
      access: "public", // Required by PutCommandOptions
    }); // Generated by Copilot

    return { valid: true, url: blob.url }; // Generated by Copilot
  } catch (e: any) {
    return { valid: false, error: e.message }; // Generated by Copilot
  }
}
// Generated by Copilot