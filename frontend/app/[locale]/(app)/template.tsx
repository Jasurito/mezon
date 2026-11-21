/**
 * Page switches ease in instead of appearing at once: a template remounts on every navigation, the layout (header,
 * footer) stays. Each top-level block of the page fades and rises slightly, also when data replaces the spinner.
 */
export default function Template({ children }: { children: React.ReactNode }) {
  return <div className="page-in">{children}</div>;
}
