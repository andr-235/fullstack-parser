"use client";

export const dynamic = 'force-dynamic';

import { useRouteAccess } from "@/shared/hooks/useRouteAccess";

import { KeywordsPage } from '@/features/keywords';

export default function Page() {
  useRouteAccess();
  return <KeywordsPage />;
}
