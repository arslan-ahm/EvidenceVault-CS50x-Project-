<script lang="ts">
  import { onMount } from 'svelte';
  import { fade, blur, fly, slide } from 'svelte/transition';
  import { gsap } from 'gsap';
  import { ScrollTrigger } from 'gsap/ScrollTrigger';

  import RelativeTime from '$lib/components/RelativeTime.svelte';
  import { apiGet } from '$lib/api';
  import { stripMarkdown } from '$lib/markdownExcerpt';
  import type { PublicOrganization, PublicReport, PublicStats } from '$lib/types';

  gsap.registerPlugin(ScrollTrigger);

  const categories = [
    { name: 'Social Media Scam', icon: 'users', desc: 'Facebook, Telegram, Instagram & WhatsApp scams', color: 'from-red-500/20 to-orange-500/20 border-red-500/20' },
    { name: 'Marketplace Fraud', icon: 'database', desc: 'Daraz, Alibaba, OLX & eBay fake listings', color: 'from-purple-500/20 to-pink-500/20 border-purple-500/20' },
    { name: 'Phishing', icon: 'fish', desc: 'Account takeovers & credential theft', color: 'from-cyan-500/20 to-teal-500/20 border-cyan-500/20' },
    { name: 'Fake Job Offers', icon: 'terminal', desc: 'Employment & freelance scams', color: 'from-amber-500/20 to-yellow-500/20 border-amber-500/20' },
    { name: 'Investment Scams', icon: 'crosshair', desc: 'Crypto & investment fraud', color: 'from-slate-500/20 to-gray-500/20 border-slate-500/20' },
    { name: 'Software & Services', icon: 'smartphone', desc: 'Software house & app service complaints', color: 'from-emerald-500/20 to-green-500/20 border-emerald-500/20' },
    { name: 'Billing Disputes', icon: 'settings', desc: 'Subscription & billing complaints', color: 'from-orange-500/20 to-amber-500/20 border-orange-500/20' },
    { name: 'Poor Service', icon: 'shield-off', desc: 'Breach of contract & bad service', color: 'from-rose-500/20 to-red-500/20 border-rose-500/20' },
    { name: 'Rental & Property', icon: 'key', desc: 'Rental & property scams', color: 'from-sky-500/20 to-blue-500/20 border-sky-500/20' },
    { name: 'Identity Theft', icon: 'lock', desc: 'Impersonation & identity fraud', color: 'from-violet-500/20 to-purple-500/20 border-violet-500/20' },
    { name: 'Delivery Scams', icon: 'cloud', desc: 'Courier & delivery fraud', color: 'from-blue-500/20 to-indigo-500/20 border-blue-500/20' },
    { name: 'Other', icon: 'alert-triangle', desc: 'General consumer complaints', color: 'from-slate-400/20 to-gray-400/20 border-slate-400/20' }
  ];

  const howItWorks = [
    { step: 1, title: 'Browse Reports', description: 'Search public scam reports and complaints across categories, organizations, and severity levels before you buy, apply, or pay.', icon: 'search' },
    { step: 2, title: 'File a Complaint', description: 'Submit a detailed complaint with evidence — screenshots, chat logs, receipts, and PDFs — plus a timeline of what happened.', icon: 'edit' },
    { step: 3, title: 'Track Progress', description: 'Follow your complaint status, view evidence timelines, and access analytics across the platform.', icon: 'bar-chart' },
    { step: 4, title: 'Warn the Community', description: 'Upvote, comment, and help others avoid the same scam or bad experience.', icon: 'globe' }
  ];

  let stats: PublicStats = {
    total_reports: 0,
    total_organizations: 0,
    resolved_reports: 0,
    pending_reports: 0,
    active_researchers: 0,
    total_evidence_items: 0
  };
  let trending: PublicReport[] = [];
  let latest: PublicReport[] = [];
  let organizations: PublicOrganization[] = [];
  let search = '';
  let loading = true;

  // Animated counter values - GSAP will tween these numbers
  let animatedReports = 0;
  let animatedOrgs = 0;
  let animatedResearchers = 0;
  let animatedResolved = 0;
  let animatedPending = 0;
  let animatedEvidence = 0;

  // Refs for GSAP animations
  let heroRef: HTMLElement;
  let statsRef: HTMLElement;
  let trendingRef: HTMLElement;
  let latestRef: HTMLElement;
  let categoriesRef: HTMLElement;
  let howItWorksRef: HTMLElement;
  let organizationsRef: HTMLElement;
  let footerRef: HTMLElement;

  const highlights = [
    { label: 'Browse Complaints', href: '/explore' },
    { label: 'File a Complaint', href: '/register' },
    { label: 'Learn More', href: '#how-it-works' }
  ];

  async function loadHomeData() {
    try {
      const [statsResponse, trendingResponse, latestResponse, organizationsResponse] = await Promise.all([
        apiGet<PublicStats>('/public/stats'),
        apiGet<PublicReport[]>('/public/reports?sort=trending&limit=6'),
        apiGet<PublicReport[]>('/public/reports?sort=recent&limit=6'),
        apiGet<PublicOrganization[]>('/public/organizations?limit=6')
      ]);

      stats = statsResponse;
      trending = trendingResponse;
      latest = latestResponse;
      organizations = organizationsResponse;
    } catch (e) {
      console.error('Failed to load home data:', e);
    } finally {
      loading = false;
    }
  }

  function animateCounters() {
    // FIXED: Use simple numeric targets with round:true at top level instead of { value, round } objects
    gsap.to(
      { reports: animatedReports, orgs: animatedOrgs, researchers: animatedResearchers,
        resolved: animatedResolved, pending: animatedPending, evidence: animatedEvidence },
      {
        duration: 2,
        reports: stats.total_reports,
        orgs: stats.total_organizations,
        researchers: stats.active_researchers,
        resolved: stats.resolved_reports,
        pending: stats.pending_reports,
        evidence: stats.total_evidence_items,
        ease: 'power3.out',
        round: true,
        onUpdate: function () {
          const target = this.targets()[0];
          animatedReports = target.reports;
          animatedOrgs = target.orgs;
          animatedResearchers = target.researchers;
          animatedResolved = target.resolved;
          animatedPending = target.pending;
          animatedEvidence = target.evidence;
        },
      }
    );
  }

  function initAnimations() {
    // Hero section entrance
    const heroTl = gsap.timeline({ defaults: { ease: 'power3.out' } });
    heroTl
      .fromTo(heroRef?.querySelector('.hero-badge'),
        { opacity: 0, y: 20, scale: 0.95 },
        { opacity: 1, y: 0, scale: 1, duration: 0.6 }
      )
      .fromTo(heroRef?.querySelector('.hero-title'),
        { opacity: 0, y: 30 },
        { opacity: 1, y: 0, duration: 0.8 },
        '-=0.3'
      )
      .fromTo(heroRef?.querySelector('.hero-subtitle'),
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.6 },
        '-=0.5'
      )
      .fromTo(heroRef?.querySelector('.hero-search'),
        { opacity: 0, y: 20, scale: 0.98 },
        { opacity: 1, y: 0, scale: 1, duration: 0.5 },
        '-=0.3'
      )
      .fromTo(heroRef?.querySelector('.hero-ctas'),
        { opacity: 0, y: 15 },
        { opacity: 1, y: 0, duration: 0.4 },
        '-=0.2'
      )
      .fromTo(heroRef?.querySelector('.hero-sidebar'),
        { opacity: 0, x: 40 },
        { opacity: 1, x: 0, duration: 0.8 },
        '-=0.6'
      );

    // Animated floating orbs
    if (heroRef) {
      const orbs = heroRef.querySelectorAll('.float-orb');
      orbs.forEach((orb, i) => {
        gsap.to(orb, {
          y: -30 + (i * 15),
          x: i % 2 === 0 ? 20 : -20,
          duration: 4 + i,
          repeat: -1,
          yoyo: true,
          ease: 'sine.inOut',
          delay: i * 0.5,
        });
      });
    }

    // Scroll-triggered section reveals
    const sections = [
      { ref: statsRef, stagger: '.stat-card', from: { y: 40, opacity: 0 }, to: { y: 0, opacity: 1, duration: 0.6 } },
      { ref: trendingRef, stagger: '.trending-card', from: { y: 30, opacity: 0 }, to: { y: 0, opacity: 1, duration: 0.5 } },
      { ref: latestRef, stagger: '.latest-item', from: { y: 20, opacity: 0 }, to: { y: 0, opacity: 1, duration: 0.4 } },
      { ref: categoriesRef, stagger: '.category-chip', from: { y: 20, opacity: 0, scale: 0.9 }, to: { y: 0, opacity: 1, scale: 1, duration: 0.4 } },
      { ref: howItWorksRef, stagger: '.step-card', from: { y: 30, opacity: 0 }, to: { y: 0, opacity: 1, duration: 0.5 } },
      { ref: organizationsRef, stagger: '.org-item', from: { y: 20, opacity: 0 }, to: { y: 0, opacity: 1, duration: 0.4 } },
    ];

    sections.forEach(({ ref, stagger, from, to }) => {
      if (!ref) return;
      const items = ref.querySelectorAll(stagger);
      if (items.length > 0) {
        gsap.set(items, from);
        ScrollTrigger.create({
          trigger: ref,
          start: 'top 85%',
          onEnter: () => {
            gsap.to(items, {
              ...to,
              stagger: 0.08,
            });
          },
          once: true,
        });
      }
    });

    // Animate the live overview sidebar
    ScrollTrigger.create({
      trigger: statsRef,
      start: 'top 80%',
      onEnter: () => animateCounters(),
      once: true,
    });
  }

  onMount(() => {
    void loadHomeData();
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        initAnimations();
      });
    });
  });

  function submitSearch() {
    const query = search.trim();
    if (!query) return;
    window.location.href = `/explore?q=${encodeURIComponent(query)}`;
  }

  function getSeverityColor(severity: string): string {
    const map: Record<string, string> = {
      critical: 'bg-red-50 text-red-700 border-red-200 dark:bg-red-500/10 dark:text-red-300 dark:border-red-500/30',
      high: 'bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-500/10 dark:text-orange-300 dark:border-orange-500/30',
      medium: 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-500/10 dark:text-amber-300 dark:border-amber-500/30',
      low: 'bg-green-50 text-green-700 border-green-200 dark:bg-green-500/10 dark:text-green-300 dark:border-green-500/30'
    };
    return map[severity?.toLowerCase()] || 'bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-500/10 dark:text-slate-300 dark:border-slate-500/30';
  }

  function getStatusColor(status: string): string {
    const map: Record<string, string> = {
      resolved: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300',
      open: 'bg-blue-50 text-blue-700 dark:bg-blue-500/10 dark:text-blue-300',
      triaged: 'bg-purple-50 text-purple-700 dark:bg-purple-500/10 dark:text-purple-300',
      in_progress: 'bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-300'
    };
    return map[status?.toLowerCase()] || 'bg-slate-100 text-slate-600 dark:bg-slate-500/10 dark:text-slate-300';
  }

  function iconSvg(name: string): string {
    const icons: Record<string, string> = {
      search: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>',
      edit: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>',
      'bar-chart': '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>',
      globe: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
      crosshair: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
      database: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4z"/></svg>',
      lock: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>',
      settings: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>',
      'shield-off': '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>',
      key: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/></svg>',
      fish: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
      terminal: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>',
      smartphone: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/></svg>',
      cloud: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z"/></svg>',
      users: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"/></svg>',
      'alert-triangle': '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>',
    };
    return icons[name] || icons['alert-triangle'];
  }
</script>

<svelte:head>
  <title>EvidenceVault | Report Scams & Consumer Complaints</title>
  <meta
    name="description"
    content="Report scams on Facebook, Telegram, Daraz, Alibaba and more. File complaints against organizations and software houses, back them with evidence, and warn the community."
  />
</svelte:head>

<!-- Animated background that covers the entire page -->
<div class="page-bg fixed inset-0 -z-10">
  <div class="absolute inset-0 bg-slate-50 dark:bg-slate-950"></div>
  <div class="animated-gradient-bg absolute inset-0 opacity-[0.07] dark:opacity-30"></div>
  <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-500/10 via-transparent to-transparent"></div>
  <div class="absolute bottom-0 left-0 right-0 h-64 bg-gradient-to-t from-slate-50 to-transparent dark:from-slate-950"></div>
</div>

<div class="relative min-h-screen text-slate-900 dark:text-white">
  <main>
    <!-- ============ HERO SECTION ============ -->
    <section bind:this={heroRef} class="relative min-h-screen overflow-hidden pt-24">
      <!-- Animated floating orbs -->
      <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div class="float-orb absolute -left-32 top-32 h-[600px] w-[600px] rounded-full bg-blue-500/10 blur-[120px]"></div>
        <div class="float-orb absolute right-0 top-60 h-[400px] w-[400px] rounded-full bg-indigo-500/10 blur-[100px]" style="animation-delay: -2s;"></div>
        <div class="float-orb absolute left-1/3 top-96 h-[300px] w-[300px] rounded-full bg-purple-500/8 blur-[80px]" style="animation-delay: -4s;"></div>
      </div>

      <div class="relative mx-auto grid max-w-7xl gap-12 px-4 pb-16 pt-16 sm:px-6 lg:grid-cols-[1.2fr_0.8fr] lg:px-8 lg:pt-24">
        <!-- Left side -->
        <div class="space-y-8">
          <div class="hero-badge inline-flex items-center gap-2.5 rounded-full border border-blue-200 bg-blue-50 px-5 py-2 shadow-sm backdrop-blur dark:border-blue-500/20 dark:bg-blue-500/10">
            <span class="flex h-2 w-2 rounded-full bg-emerald-400">
              <span class="h-2 w-2 animate-ping rounded-full bg-emerald-400"></span>
            </span>
            <span class="text-xs font-semibold uppercase tracking-[0.15em] text-blue-700 dark:text-blue-300">Trusted complaint platform</span>
          </div>

          <div class="space-y-6">
            <h1 class="hero-title text-5xl font-bold leading-tight tracking-tight sm:text-6xl lg:text-7xl">
              Expose every
              <br />
              <span class="gradient-text">scam</span> for
              <br />
              the <span class="gradient-text">community</span>.
            </h1>
            <p class="hero-subtitle max-w-2xl text-lg leading-relaxed text-slate-600 dark:text-slate-400">
              EvidenceVault empowers people to report scams on social platforms and marketplaces,
              file complaints against organizations, and track them with a modern, public-first workflow.
            </p>
          </div>

          <!-- Search -->
          <div class="hero-search group flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white/60 p-3 shadow-lg shadow-blue-500/5 backdrop-blur transition-all duration-300 focus-within:border-blue-400 focus-within:shadow-blue-500/10 dark:border-slate-700/60 dark:bg-slate-800/60 dark:focus-within:border-blue-500/50 sm:flex-row">
            <div class="relative flex-1">
              <svg class="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400 dark:text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
              <input
                class="w-full rounded-xl border-0 bg-transparent py-3 pl-11 pr-4 text-base text-slate-900 outline-none placeholder:text-slate-400 focus:ring-0 dark:text-white dark:placeholder:text-slate-500"
                bind:value={search}
                placeholder="Search scams, organizations, and complaints..."
                maxlength={200}
                on:keydown={(event) => event.key === 'Enter' && submitSearch()}
                aria-label="Search public reports"
              />
            </div>
            <button class="button-primary shrink-0 px-6 py-3 text-base" on:click={submitSearch}>Search</button>
          </div>

          <!-- CTA buttons -->
          <div class="hero-ctas flex flex-wrap gap-3">
            {#each highlights as item}
              <a class="group relative overflow-hidden rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-600 shadow-sm transition-all duration-300 hover:border-blue-300 hover:text-slate-900 hover:shadow-md dark:border-slate-700/60 dark:bg-slate-800/50 dark:text-slate-300 dark:hover:border-blue-500/30 dark:hover:text-white" href={item.href}>
                <span class="relative z-10">{item.label}</span>
                <div class="absolute inset-0 -translate-x-full bg-gradient-to-r from-blue-500/10 to-indigo-500/10 transition-transform duration-500 group-hover:translate-x-0"></div>
              </a>
            {/each}
          </div>

          <!-- Quick Stats -->
          <div bind:this={statsRef} class="stats-grid grid gap-3 sm:grid-cols-3">
            <div class="stat-card rounded-2xl border border-slate-200 bg-white/70 p-4 shadow-sm backdrop-blur transition-all duration-300 hover:border-blue-300 dark:border-slate-700/60 dark:bg-slate-800/40 dark:hover:border-blue-500/30">
              <div class="flex items-center gap-2">
                <svg class="h-4 w-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                <p class="text-xs font-medium uppercase tracking-[0.12em] text-slate-500 dark:text-slate-400">Total Reports</p>
              </div>
              <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
                {#if loading}
                  <span class="skeleton inline-block h-8 w-16 rounded"></span>
                {:else}
                  {animatedReports}
                {/if}
              </p>
            </div>
            <div class="stat-card rounded-2xl border border-slate-200 bg-white/70 p-4 shadow-sm backdrop-blur transition-all duration-300 hover:border-blue-300 dark:border-slate-700/60 dark:bg-slate-800/40 dark:hover:border-blue-500/30">
              <div class="flex items-center gap-2">
                <svg class="h-4 w-4 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
                <p class="text-xs font-medium uppercase tracking-[0.12em] text-slate-500 dark:text-slate-400">Organizations</p>
              </div>
              <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
                {#if loading}
                  <span class="skeleton inline-block h-8 w-16 rounded"></span>
                {:else}
                  {animatedOrgs}
                {/if}
              </p>
            </div>
            <div class="stat-card rounded-2xl border border-slate-200 bg-white/70 p-4 shadow-sm backdrop-blur transition-all duration-300 hover:border-blue-300 dark:border-slate-700/60 dark:bg-slate-800/40 dark:hover:border-blue-500/30">
              <div class="flex items-center gap-2">
                <svg class="h-4 w-4 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"/></svg>
                <p class="text-xs font-medium uppercase tracking-[0.12em] text-slate-500 dark:text-slate-400">Reporters</p>
              </div>
              <p class="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
                {#if loading}
                  <span class="skeleton inline-block h-8 w-16 rounded"></span>
                {:else}
                  {animatedResearchers}
                {/if}
              </p>
            </div>
          </div>
        </div>

        <!-- Right side: Live Overview -->
        <div class="hero-sidebar">
          <div class="relative overflow-hidden rounded-2xl border border-slate-200 bg-white/60 p-6 shadow-xl backdrop-blur dark:border-slate-700/60 dark:bg-slate-800/30">
            <div class="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-indigo-500/5 to-purple-500/5"></div>
            <div class="relative space-y-5">
              <div class="flex items-center gap-2">
                <span class="flex h-2.5 w-2.5 rounded-full bg-emerald-400"><span class="h-2.5 w-2.5 animate-ping rounded-full bg-emerald-400"></span></span>
                <p class="text-xs font-bold uppercase tracking-[0.2em] text-blue-700 dark:text-blue-300">Live Overview</p>
              </div>

              <div class="grid gap-4 sm:grid-cols-2">
                <div class="rounded-2xl bg-slate-100/80 p-5 shadow-sm transition-all duration-300 hover:shadow-md dark:bg-slate-800/60">
                  <div class="flex items-center gap-2">
                    <span class="text-xs uppercase tracking-[0.16em] text-slate-500 dark:text-slate-400">Resolved</span>
                    <span class="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-semibold text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300">✓</span>
                  </div>
                  <p class="mt-2 text-3xl font-bold text-slate-900 dark:text-white">
                    {#if loading}
                      <span class="skeleton inline-block h-8 w-16 rounded"></span>
                    {:else}
                      {animatedResolved}
                    {/if}
                  </p>
                </div>
                <div class="rounded-2xl bg-slate-100/80 p-5 shadow-sm transition-all duration-300 hover:shadow-md dark:bg-slate-800/60">
                  <div class="flex items-center gap-2">
                    <span class="text-xs uppercase tracking-[0.16em] text-slate-500 dark:text-slate-400">Pending</span>
                    <span class="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-semibold text-amber-700 dark:bg-amber-500/10 dark:text-amber-300">
                      <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                    </span>
                  </div>
                  <p class="mt-2 text-3xl font-bold text-slate-900 dark:text-white">
                    {#if loading}
                      <span class="skeleton inline-block h-8 w-16 rounded"></span>
                    {:else}
                      {animatedPending}
                    {/if}
                  </p>
                </div>
                <div class="rounded-2xl bg-slate-100/80 p-5 shadow-sm transition-all duration-300 hover:shadow-md dark:bg-slate-800/60 sm:col-span-2">
                  <div class="flex items-center gap-2">
                    <span class="text-xs uppercase tracking-[0.16em] text-slate-500 dark:text-slate-400">Evidence Items</span>
                    <span class="rounded-full bg-indigo-100 px-2 py-0.5 text-[10px] font-semibold text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-300">
                      <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"/></svg>
                    </span>
                  </div>
                  <p class="mt-2 text-3xl font-bold text-slate-900 dark:text-white">
                    {#if loading}
                      <span class="skeleton inline-block h-8 w-16 rounded"></span>
                    {:else}
                      {animatedEvidence}
                    {/if}
                  </p>
                </div>
              </div>

              <div class="rounded-2xl border border-blue-200 bg-gradient-to-br from-blue-500/10 to-indigo-500/10 p-4 dark:border-blue-500/10">
                <div class="flex items-start gap-3">
                  <svg class="mt-0.5 h-6 w-6 shrink-0 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                  <div>
                    <p class="text-sm font-semibold text-slate-900 dark:text-white">Community-driven complaint platform</p>
                    <p class="mt-1 text-xs leading-relaxed text-slate-500 dark:text-slate-400">
                      Built for consumers, organizations, and the community to expose scams together.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ============ TRENDING & LATEST ============ -->
    <section class="mx-auto max-w-7xl px-4 pb-20 sm:px-6 lg:px-8">
      <div class="grid gap-8 lg:grid-cols-[1fr_1fr]">
        <!-- Trending Cases -->
        <div bind:this={trendingRef} class="space-y-5">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs font-bold uppercase tracking-[0.2em] text-blue-700 dark:text-blue-300">Trending Now</p>
              <h2 class="mt-1 text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Most discussed complaints</h2>
            </div>
            <a class="group flex items-center gap-1 text-sm font-semibold text-blue-600 transition-colors hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300" href="/explore">
              View all
              <span class="inline-block transition-transform group-hover:translate-x-0.5">→</span>
            </a>
          </div>

          {#if loading}
            <div class="grid gap-4 md:grid-cols-2">
              {#each [1, 2, 3, 4] as _}
                <div class="skeleton h-44 rounded-2xl"></div>
              {/each}
            </div>
          {:else if trending.length === 0}
            <div class="rounded-2xl border border-slate-200 bg-white/60 p-8 text-center text-sm text-slate-500 dark:border-slate-700/60 dark:bg-slate-800/30 dark:text-slate-400">
              <svg class="mx-auto mb-2 h-8 w-8 text-slate-400 dark:text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/></svg>
              <p>No trending reports yet. Be the first to submit!</p>
            </div>
          {:else}
            <div class="grid gap-4 md:grid-cols-2">
              {#each trending as item, i}
                <a
                  class="trending-card group rounded-2xl border border-slate-200 bg-white/70 p-5 shadow-sm backdrop-blur transition-all duration-300 hover:border-blue-300 hover:bg-white dark:border-slate-700/60 dark:bg-slate-800/40 dark:hover:border-blue-500/30 dark:hover:bg-slate-800/60"
                  href={`/explore/${item.id}`}
                  style="transition-delay: {i * 80}ms"
                >
                  <div class="flex items-start justify-between gap-3">
                    <div class="min-w-0">
                      <p class="text-[10px] font-bold uppercase tracking-[0.18em] text-blue-700 dark:text-blue-300">{item.category}</p>
                      <h3 class="mt-1.5 truncate text-base font-bold text-slate-900 dark:text-white">{item.title}</h3>
                    </div>
                    <span class="shrink-0 rounded-full border px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wide {getSeverityColor(item.severity)}">
                      {item.severity}
                    </span>
                  </div>
                  <p class="mt-3 line-clamp-2 text-sm leading-relaxed text-slate-500 dark:text-slate-400">
                    {item.description ? stripMarkdown(item.description) : 'No summary available yet.'}
                  </p>
                  <div class="mt-4 flex items-center gap-3 text-xs text-slate-400 dark:text-slate-500">
                    <span class="flex items-center gap-1">
                      <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                      {item.views_count}
                    </span>
                    <span class="flex items-center gap-1">
                      <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"/></svg>
                      {item.upvotes_count}
                    </span>
                    <RelativeTime date={item.created_at} className="ml-auto" />
                  </div>
                </a>
              {/each}
            </div>
          {/if}
        </div>

        <!-- Latest Reports -->
        <div bind:this={latestRef} class="space-y-5">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs font-bold uppercase tracking-[0.2em] text-blue-700 dark:text-blue-300">Latest Activity</p>
              <h2 class="mt-1 text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Recent submissions</h2>
            </div>
            <a class="group flex items-center gap-1 text-sm font-semibold text-blue-600 transition-colors hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300" href="/explore">
              See all
              <span class="inline-block transition-transform group-hover:translate-x-0.5">→</span>
            </a>
          </div>

          {#if loading}
            <div class="space-y-3">
              {#each [1, 2, 3, 4] as _}
                <div class="skeleton h-20 rounded-2xl"></div>
              {/each}
            </div>
          {:else if latest.length === 0}
            <div class="rounded-2xl border border-slate-200 bg-white/60 p-8 text-center text-sm text-slate-500 dark:border-slate-700/60 dark:bg-slate-800/30 dark:text-slate-400">
              <svg class="mx-auto mb-2 h-8 w-8 text-slate-400 dark:text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/></svg>
              <p>No reports yet. Submit the first one!</p>
            </div>
          {:else}
            <div class="space-y-3">
              {#each latest as item, i}
                <a
                  class="latest-item group flex items-center justify-between gap-4 rounded-2xl border border-slate-200 bg-white/70 p-4 shadow-sm backdrop-blur transition-all duration-300 hover:border-blue-300 hover:bg-white dark:border-slate-700/60 dark:bg-slate-800/40 dark:hover:border-blue-500/30 dark:hover:bg-slate-800/60"
                  href={`/explore/${item.id}`}
                  style="transition-delay: {i * 60}ms"
                >
                  <div class="min-w-0 flex-1">
                    <div class="flex items-center gap-2">
                      <h3 class="truncate font-bold text-slate-900 dark:text-white">{item.title}</h3>
                      <span class="shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold {getStatusColor(item.status)}">
                        {item.status.replace('_', ' ')}
                      </span>
                    </div>
                    <p class="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
                      {item.organization_name || 'Community report'}
                      <span class="mx-1.5">·</span>
                      <span class="text-[10px] font-medium uppercase tracking-wider text-slate-400 dark:text-slate-500">{item.category}</span>
                    </p>
                  </div>
                  <div class="hidden shrink-0 items-center gap-3 text-xs text-slate-400 dark:text-slate-500 sm:flex">
                    <span class="flex items-center gap-1">
                      <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                      {item.views_count}
                    </span>
                    <span class="flex items-center gap-1">
                      <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"/></svg>
                      {item.upvotes_count}
                    </span>
                  </div>
                  <RelativeTime date={item.created_at} className="shrink-0 text-xs text-slate-400 dark:text-slate-500" />
                </a>
              {/each}
            </div>
          {/if}
        </div>
      </div>
    </section>

    <!-- ============ HOW IT WORKS ============ -->
    <section bind:this={howItWorksRef} id="how-it-works" class="relative overflow-hidden py-20">
      <div class="absolute inset-0 bg-gradient-to-b from-blue-500/5 via-transparent to-transparent"></div>
      <div class="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="mx-auto max-w-2xl text-center">
          <p class="text-xs font-bold uppercase tracking-[0.2em] text-blue-700 dark:text-blue-300">How It Works</p>
          <h2 class="mt-3 text-3xl font-bold tracking-tight text-slate-900 dark:text-white sm:text-4xl">
            From complaint to resolution
          </h2>
          <p class="mt-4 text-lg leading-relaxed text-slate-600 dark:text-slate-400">
            A simple, transparent workflow for reporting scams and filing complaints.
          </p>
        </div>

        <div class="relative mt-16">
          <!-- Connecting line -->
          <div class="absolute left-1/2 top-0 hidden h-full w-px bg-gradient-to-b from-blue-500/20 via-indigo-500/20 to-purple-500/20 lg:block"></div>

          <div class="grid gap-8 lg:grid-cols-4">
            {#each howItWorks as step, i}
              <div class="step-card group relative text-center">
                <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/20 transition-all duration-500 group-hover:scale-110 group-hover:shadow-xl group-hover:shadow-blue-500/30">
                  {@html iconSvg(step.icon)}
                </div>
                <div class="mt-2 hidden lg:block">
                  <div class="mx-auto h-8 w-px bg-gradient-to-b from-blue-500/20 to-transparent"></div>
                </div>
                <div class="mt-4 rounded-2xl border border-slate-200 bg-white/70 p-5 shadow-sm backdrop-blur transition-all duration-300 group-hover:border-blue-300 group-hover:shadow-md dark:border-slate-700/60 dark:bg-slate-800/40 dark:group-hover:border-blue-500/30">
                  <span class="inline-flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700 dark:bg-blue-500/20 dark:text-blue-300">0{step.step}</span>
                  <h3 class="mt-3 text-lg font-bold text-slate-900 dark:text-white">{step.title}</h3>
                  <p class="mt-2 text-sm leading-relaxed text-slate-500 dark:text-slate-400">{step.description}</p>
                </div>
              </div>
            {/each}
          </div>
        </div>
      </div>
    </section>

    <!-- ============ COMPLAINT CATEGORIES ============ -->
    <section bind:this={categoriesRef} class="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-2xl text-center">
        <p class="text-xs font-bold uppercase tracking-[0.2em] text-blue-700 dark:text-blue-300">Categories</p>
        <h2 class="mt-3 text-3xl font-bold tracking-tight text-slate-900 dark:text-white sm:text-4xl">
          Browse by scam & complaint type
        </h2>
        <p class="mt-4 text-lg leading-relaxed text-slate-600 dark:text-slate-400">
          Explore complaints across a wide range of scam and consumer-complaint categories.
        </p>
      </div>

      <div class="mt-12 grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {#each categories as cat, i}
          <a
            class="category-chip group relative overflow-hidden rounded-2xl border bg-gradient-to-br {cat.color} p-5 backdrop-blur transition-all duration-500 hover:shadow-lg hover:shadow-blue-500/5"
            href="/explore?category={cat.name}"
            style="transition-delay: {i * 50}ms"
          >
            <div class="absolute -right-6 -top-6 h-20 w-20 rounded-full bg-white/5 transition-all duration-500 group-hover:scale-[3]"></div>
            <div class="relative z-10">
              <span class="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-white/40 text-slate-600 dark:bg-white/10 dark:text-slate-300">
                {@html iconSvg(cat.icon)}
              </span>
              <h3 class="mt-3 text-sm font-bold text-slate-900 dark:text-white">{cat.name}</h3>
              <p class="mt-1 text-xs text-slate-600 dark:text-slate-400">{cat.desc}</p>
            </div>
          </a>
        {/each}
      </div>
    </section>

    <!-- ============ FEATURED ORGANIZATIONS ============ -->
    <section bind:this={organizationsRef} class="py-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="mx-auto max-w-2xl text-center">
          <p class="text-xs font-bold uppercase tracking-[0.2em] text-blue-700 dark:text-blue-300">Organizations</p>
          <h2 class="mt-3 text-3xl font-bold tracking-tight text-slate-900 dark:text-white sm:text-4xl">
            Most reported organizations
          </h2>
          <p class="mt-4 text-lg leading-relaxed text-slate-600 dark:text-slate-400">
            Platforms, companies, and organizations the community has filed complaints against.
          </p>
        </div>

        <div class="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {#if loading}
            {#each [1, 2, 3] as _}
              <div class="skeleton h-32 rounded-2xl"></div>
            {/each}
          {:else if organizations.length === 0}
            <div class="col-span-full rounded-2xl border border-slate-200 bg-white/60 p-12 text-center text-sm text-slate-500 dark:border-slate-700/60 dark:bg-slate-800/30 dark:text-slate-400">
              <svg class="mx-auto mb-3 h-8 w-8 text-slate-400 dark:text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
              <p>No organizations registered yet.</p>
            </div>
          {:else}
            {#each organizations as org, i}
              <div
                class="org-item rounded-2xl border border-slate-200 bg-white/70 p-5 shadow-sm backdrop-blur transition-all duration-300 hover:border-blue-300 dark:border-slate-700/60 dark:bg-slate-800/40 dark:hover:border-blue-500/30"
                style="transition-delay: {i * 80}ms"
              >
                <div class="flex items-start justify-between gap-3">
                  <div class="min-w-0">
                    <div class="flex items-center gap-2">
                      <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 text-xs font-bold text-white">
                        {org.name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <h3 class="truncate font-bold text-slate-900 dark:text-white">{org.name}</h3>
                        <p class="text-xs text-slate-500 dark:text-slate-400">{org.industry || 'Organization'}</p>
                      </div>
                    </div>
                  </div>
                  <span class="shrink-0 rounded-full bg-blue-50 px-3 py-1 text-xs font-bold text-blue-700 dark:bg-blue-500/10 dark:text-blue-300">
                    {org.total_reports} reports
                  </span>
                </div>
                <div class="mt-4 flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400">
                  <span class="flex items-center gap-1">
                    <svg class="h-3.5 w-3.5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                    {org.resolved_reports} resolved
                  </span>
                  <span class="flex items-center gap-1">
                    <svg class="h-3.5 w-3.5 text-slate-400 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/></svg>
                    {org.open_reports} open
                  </span>
                  {#if org.website}
                    <a href={org.website} target="_blank" rel="noreferrer" class="ml-auto text-blue-600 hover:underline dark:text-blue-400">Website →</a>
                  {/if}
                </div>
              </div>
            {/each}
          {/if}
        </div>
      </div>
    </section>
  </main>

  <!-- ============ FOOTER ============ -->
  <footer bind:this={footerRef} class="border-t border-slate-200 bg-white dark:border-slate-800/60 dark:bg-slate-950">
    <div class="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <div class="grid gap-10 lg:grid-cols-[1.5fr_1fr_1fr_1fr]">
        <!-- Brand -->
        <div class="space-y-4">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 text-base font-bold text-white shadow-lg">
              EV
            </div>
            <div>
              <p class="text-lg font-bold text-slate-900 dark:text-white">EvidenceVault</p>
              <p class="text-xs font-medium uppercase tracking-[0.2em] text-blue-600 dark:text-blue-400">Report Scams & Complaints</p>
            </div>
          </div>
          <p class="max-w-xs text-sm leading-relaxed text-slate-500 dark:text-slate-400">
            A modern platform for reporting scams and filing complaints,
            backed by real evidence and a community that helps each other.
          </p>
          <div class="flex items-center gap-4">
            <a href="/" rel="nofollow" class="text-slate-400 transition-colors hover:text-blue-600 dark:text-slate-500 dark:hover:text-blue-400" aria-label="Twitter">
              <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
            </a>
            <a href="/" rel="nofollow" class="text-slate-400 transition-colors hover:text-blue-600 dark:text-slate-500 dark:hover:text-blue-400" aria-label="GitHub">
              <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 21.795 24 17.295 24 12 24 5.37 18.63 0 12 0z"/></svg>
            </a>
            <a href="/" rel="nofollow" class="text-slate-400 transition-colors hover:text-blue-600 dark:text-slate-500 dark:hover:text-blue-400" aria-label="LinkedIn">
              <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
            </a>
          </div>
        </div>

        <!-- Platform -->
        <div>
          <h4 class="text-sm font-bold uppercase tracking-[0.12em] text-slate-700 dark:text-slate-300">Platform</h4>
          <ul class="mt-5 space-y-3">
            <li><a href="/explore" class="text-sm text-slate-500 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-white">Explore Complaints</a></li>
            <li><a href="/register" class="text-sm text-slate-500 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-white">File a Complaint</a></li>
            <li><a href="/explore" class="text-sm text-slate-500 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-white">Search</a></li>
            <li><a href="/dashboard" class="text-sm text-slate-500 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-white">Dashboard</a></li>
          </ul>
        </div>

        <!-- Resources -->
        <div>
          <h4 class="text-sm font-bold uppercase tracking-[0.12em] text-slate-700 dark:text-slate-300">Resources</h4>
          <ul class="mt-5 space-y-3">
            <li><span role="link" tabindex="0" class="text-sm text-slate-500 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-white cursor-pointer">Documentation</span></li>
            <li><span role="link" tabindex="0" class="text-sm text-slate-500 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-white cursor-pointer">API Reference</span></li>
            <li><span role="link" tabindex="0" class="text-sm text-slate-500 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-white cursor-pointer">Safety Guide</span></li>
            <li><span role="link" tabindex="0" class="text-sm text-slate-500 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-white cursor-pointer">How It Works</span></li>
          </ul>
        </div>

        <!-- Company -->
        <div>
          <h4 class="text-sm font-bold uppercase tracking-[0.12em] text-slate-700 dark:text-slate-300">Company</h4>
          <ul class="mt-5 space-y-3">
            <li><span role="link" tabindex="0" class="text-sm text-slate-500 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-white cursor-pointer">About</span></li>
            <li><span role="link" tabindex="0" class="text-sm text-slate-500 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-white cursor-pointer">Privacy Policy</span></li>
            <li><span role="link" tabindex="0" class="text-sm text-slate-500 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-white cursor-pointer">Terms of Service</span></li>
            <li><span role="link" tabindex="0" class="text-sm text-slate-500 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-white cursor-pointer">Contact</span></li>
          </ul>
        </div>
      </div>

      <div class="mt-12 border-t border-slate-200 pt-8 dark:border-slate-800">
        <div class="flex flex-col items-center justify-between gap-4 sm:flex-row">
          <p class="text-xs text-slate-400 dark:text-slate-500">
            © {new Date().getFullYear()} EvidenceVault. All rights reserved.
          </p>
          <div class="flex items-center gap-6 text-xs text-slate-400 dark:text-slate-500">
            <span role="link" tabindex="0" class="transition-colors hover:text-slate-700 dark:hover:text-slate-300 cursor-pointer">Privacy</span>
            <span role="link" tabindex="0" class="transition-colors hover:text-slate-700 dark:hover:text-slate-300 cursor-pointer">Terms</span>
            <span role="link" tabindex="0" class="transition-colors hover:text-slate-700 dark:hover:text-slate-300 cursor-pointer">Cookies</span>
          </div>
          <p class="text-xs text-slate-400 dark:text-slate-500">
            Built for the community 🌐
          </p>
        </div>
      </div>
    </div>
  </footer>
</div>

<style>
  :global(.page-bg) {
    z-index: -10;
  }
  :global(.animated-gradient-bg) {
    background: linear-gradient(135deg, #1e3a5f, #0f172a, #1a1f3a, #0f172a, #1e3a5f);
    background-size: 400% 400%;
    animation: gradientShift 15s ease infinite;
  }
  :global([data-theme='light'] .animated-gradient-bg) {
    background: linear-gradient(135deg, #bfdbfe, #eff6ff, #e0e7ff, #eff6ff, #bfdbfe);
    background-size: 400% 400%;
    animation: gradientShift 15s ease infinite;
  }
  @keyframes gradientShift {
    0% { background-position: 0% 50%; }
    25% { background-position: 100% 0%; }
    50% { background-position: 100% 100%; }
    75% { background-position: 0% 100%; }
    100% { background-position: 0% 50%; }
  }
</style>