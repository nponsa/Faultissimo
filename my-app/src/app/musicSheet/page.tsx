"use client";
import Link from "next/link";
import { useCallback } from "react";




export default function MusicSheetPage() {
    // Example DOM-router style navigation (full page navigation)
    const goHomeWithDOM = useCallback(() => {
        // uses the browser DOM to navigate — works even outside Next.js routers
        window.location.assign("/");
    }, []);

    return (
        <main style={{ padding: 24, fontFamily: "system-ui, sans-serif" }}>
            <h1>Music Sheet</h1>
            <p>This is the /musicSheet page.</p>

            <div style={{ display: "flex", gap: 12, marginTop: 18 }}>
                {/* Next.js client-side navigation */}
                <Link href="/">
                    <button type="button">Go to Home (next/link)</button>
                </Link>

                {/* DOM-style navigation (uses browser API) */}
                <button type="button" onClick={goHomeWithDOM}>
                    Go to Home (DOM)
                </button>
            </div>
        </main>
    );
}