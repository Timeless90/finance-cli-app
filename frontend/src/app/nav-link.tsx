import { Link, useLocation } from '@tanstack/react-router';
import type { ReactNode } from 'react';
export function NavLink({
  to,
  className,
  children,
}: {
  to: string;
  className: string | ((state: { isActive: boolean }) => string);
  children: ReactNode;
}) {
  const { pathname } = useLocation();
  const isActive = pathname === to || pathname.startsWith(to + '/');
  return (
    <Link
      to={to}
      aria-current={isActive ? 'page' : undefined}
      className={typeof className === 'function' ? className({ isActive }) : className}
    >
      {children}
    </Link>
  );
}
