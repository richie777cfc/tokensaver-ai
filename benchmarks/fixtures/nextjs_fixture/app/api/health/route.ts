import { NextResponse } from "next/server";

export async function GET() {
  const dbUrl = process.env.DATABASE_URL;
  return NextResponse.json({ status: "ok", db: !!dbUrl });
}
