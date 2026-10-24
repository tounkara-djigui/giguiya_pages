import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { SITE } from '../../core/config';
import { MemberService } from '../../core/services/member.service';
import { apiError } from '../../core/utils/api.utils';
import { PageHeaderComponent } from '../../shared/components/page-header/page-header.component';
import { Icons } from '../../shared/icons';

@Component({
  selector: 'app-become-member-page',
  imports: [ReactiveFormsModule, RouterLink, LucideAngularModule, PageHeaderComponent],
  templateUrl: './become-member.page.html',
  styles: `
    .fees { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .fee { padding: 24px; }
    .steps { list-style: none; padding: 0; margin: 0; display: grid; gap: 18px; counter-reset: s; }
    .steps li { display: flex; gap: 16px; align-items: flex-start; }
    .steps .n { width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0; display: grid; place-items: center; border: 1px solid var(--gold-border-strong); color: var(--gold); font-family: var(--font-mono); font-size: .8rem; }
    .steps p { color: var(--text-2); font-size: .95rem; }
    .steps strong { color: var(--text); font-weight: 500; display: block; }
    .form-card { overflow: hidden; }
    .rel { position: relative; }
    .ok { width: 80px; height: 80px; margin: 0 auto; border-radius: 50%; display: grid; place-items: center; background: rgba(16,185,129,.12); color: var(--green); border: 1px solid rgba(16,185,129,.4); }
    .gold { color: var(--gold-light); font-weight: 500; }
    .sep { font-family: var(--font-mono); font-size: .7rem; letter-spacing: .18em; text-transform: uppercase; color: var(--gold); margin-top: 8px; }
  `,
})
export default class BecomeMemberPage {
  private fb = inject(FormBuilder);
  private api = inject(MemberService);
  protected readonly i = Icons;
  protected readonly site = SITE;
  protected loading = signal(false);
  protected error = signal('');
  protected done = signal<{ email: string; emailSent: boolean } | null>(null);
  protected form = this.fb.nonNullable.group({
    first_name: ['', Validators.required],
    last_name: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    phone: [''],
    birth_date: [''],
    birth_place: [''],
    fiscal_code: ['', Validators.maxLength(20)],
    address: [''],
    city: [''],
    privacy_accepted: [false, Validators.requiredTrue],
  });

  bad(name: keyof typeof this.form.controls): boolean {
    const c = this.form.controls[name];
    return c.invalid && c.touched;
  }

  submit(): void {
    this.form.markAllAsTouched();
    if (this.form.invalid) return;
    this.loading.set(true);
    this.error.set('');
    const v = this.form.getRawValue();
    const clean = (s: string) => s.trim() || null;
    this.api
      .register({
        first_name: v.first_name.trim(), last_name: v.last_name.trim(), email: v.email.trim(),
        phone: clean(v.phone), birth_date: clean(v.birth_date), birth_place: clean(v.birth_place),
        fiscal_code: clean(v.fiscal_code), address: clean(v.address), city: clean(v.city),
        privacy_accepted: v.privacy_accepted,
      })
      .subscribe({
        next: (r) => {
          this.loading.set(false);
          this.done.set({ email: v.email, emailSent: !!r.email_sent });
          window.scrollTo({ top: 0, behavior: 'smooth' });
        },
        error: (e) => {
          this.loading.set(false);
          this.error.set(apiError(e));
        },
      });
  }
}
