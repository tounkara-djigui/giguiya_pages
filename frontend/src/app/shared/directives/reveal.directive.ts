import { AfterViewInit, Directive, ElementRef, OnDestroy, inject, input } from '@angular/core';

@Directive({ selector: '[appReveal]' })
export class RevealDirective implements AfterViewInit, OnDestroy {
  private el = inject(ElementRef<HTMLElement>);
  private observer?: IntersectionObserver;
  readonly revealDelay = input(0);

  ngAfterViewInit(): void {
    const node = this.el.nativeElement as HTMLElement;
    node.classList.add('reveal');
    node.style.transitionDelay = `${this.revealDelay()}ms`;
    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            node.classList.add('is-visible');
            this.observer?.disconnect();
          }
        });
      },
      { threshold: 0.12 },
    );
    this.observer.observe(node);
  }

  ngOnDestroy(): void {
    this.observer?.disconnect();
  }
}
