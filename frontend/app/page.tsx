"use client";

import { useState } from "react";

export default function Home() {
  const [userEmail, setUserEmail] = useState<string>("");
  const [subscribed, setSubscribed] = useState(false);
  const [notificationFrequency, setNotificationFrequency] = useState("weekly");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubscribe = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userEmail) return;

    setIsSubmitting(true);
    try {
      const response = await fetch("http://localhost:8000/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: userEmail,
          notification_frequency: notificationFrequency,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setSubscribed(true);
        }
      }
    } catch (err) {
      console.error("Error subscribing:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center relative overflow-hidden">
      {/* Subtle background pattern */}
      <div className="absolute inset-0 opacity-[0.02] bg-[linear-gradient(to_right,#808080_1px,transparent_1px),linear-gradient(to_bottom,#808080_1px,transparent_1px)] bg-[size:4rem_4rem]"></div>
      
      <div className="container mx-auto px-4 py-12 relative z-10">
        {/* Header */}
        <header className="text-center mb-16">
          <h1 className="text-6xl md:text-7xl font-light tracking-tight text-[#f5f5f5] mb-6 uppercase letter-spacing-wider">
            FastFit
          </h1>
          <div className="w-24 h-px bg-[#d4af37] mx-auto mb-6"></div>
          <p className="text-lg md:text-xl text-[#a0a0a0] font-light tracking-wide">
            Personalized style notifications
          </p>
        </header>

        {/* Subscription Form */}
        {!subscribed ? (
          <div className="max-w-lg mx-auto bg-[#1a1a1a] border border-[#333333] p-10 md:p-12">
            <h2 className="text-2xl font-light text-[#f5f5f5] mb-2 tracking-wide uppercase">Join</h2>
            <p className="text-[#a0a0a0] mb-8 text-sm font-light leading-relaxed">
              Receive curated notifications about new releases that match your personal style.
            </p>
            <form onSubmit={handleSubscribe} className="space-y-6">
              <div>
                <label htmlFor="email" className="block text-xs uppercase tracking-wider text-[#a0a0a0] mb-3 font-light">
                  Email Address
                </label>
                <input
                  type="email"
                  id="email"
                  value={userEmail}
                  onChange={(e) => setUserEmail(e.target.value)}
                  required
                  className="w-full px-4 py-3 bg-[#0a0a0a] border border-[#333333] text-[#f5f5f5] placeholder:text-[#555555] focus:outline-none focus:border-[#d4af37] transition-colors font-light"
                  placeholder="your@email.com"
                />
              </div>
              <div>
                <label htmlFor="frequency" className="block text-xs uppercase tracking-wider text-[#a0a0a0] mb-3 font-light">
                  Notification Frequency
                </label>
                <select
                  id="frequency"
                  value={notificationFrequency}
                  onChange={(e) => setNotificationFrequency(e.target.value)}
                  className="w-full px-4 py-3 bg-[#0a0a0a] border border-[#333333] text-[#f5f5f5] focus:outline-none focus:border-[#d4af37] transition-colors font-light appearance-none cursor-pointer"
                >
                  <option value="daily" className="bg-[#1a1a1a]">Daily</option>
                  <option value="weekly" className="bg-[#1a1a1a]">Weekly</option>
                  <option value="realtime" className="bg-[#1a1a1a]">As soon as new releases are detected</option>
                </select>
              </div>
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-[#d4af37] text-[#0a0a0a] py-4 font-light tracking-wider uppercase text-sm hover:bg-[#f4d03f] transition-colors disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-[#d4af37]"
              >
                {isSubmitting ? "Subscribing..." : "Subscribe"}
              </button>
            </form>
          </div>
        ) : (
          <div className="max-w-lg mx-auto bg-[#1a1a1a] border border-[#333333] p-10 md:p-12 text-center">
            <div className="text-5xl mb-6 text-[#d4af37]">✓</div>
            <h2 className="text-2xl font-light text-[#f5f5f5] mb-4 tracking-wide uppercase">Welcome</h2>
            <div className="w-16 h-px bg-[#d4af37] mx-auto mb-6"></div>
            <p className="text-[#a0a0a0] mb-2 font-light text-sm">
              We've sent a welcome email to <span className="text-[#f5f5f5]">{userEmail}</span>
            </p>
            <p className="text-[#666666] text-xs font-light mt-4">
              Check your inbox for personalized fashion recommendations.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
