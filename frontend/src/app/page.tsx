import { redirect } from "next/navigation";

// Root → redirect to dashboard (auth middleware handles unauthenticated)
export default function Home() {
  redirect("/dashboard");
}
