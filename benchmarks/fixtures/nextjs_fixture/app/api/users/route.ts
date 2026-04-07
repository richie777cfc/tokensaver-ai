import { NextResponse } from "next/server";

const API_SECRET = process.env.API_SECRET;

export async function GET() {
  return NextResponse.json({ users: [] });
}

export async function POST(request: Request) {
  const body = await request.json();
  return NextResponse.json({ created: true, name: body.name }, { status: 201 });
}
