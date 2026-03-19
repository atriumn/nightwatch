import { createMDX } from 'fumadocs-mdx/next';
import { resolve } from 'path';

/** @type {import('next').NextConfig} */
const config = {
  reactStrictMode: true,
  outputFileTracingRoot: resolve(import.meta.dirname, '..'),
};

const withMDX = createMDX();

export default withMDX(config);
