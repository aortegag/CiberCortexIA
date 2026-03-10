/** @type {import('next').NextConfig} */
const nextConfig = {
  // Standalone output para Docker multi-stage (Stage 3: runner)
  output: "standalone",

  // API rewrite → proxied to backend en desarrollo local
  // En producción, nginx hace el proxy directamente
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
