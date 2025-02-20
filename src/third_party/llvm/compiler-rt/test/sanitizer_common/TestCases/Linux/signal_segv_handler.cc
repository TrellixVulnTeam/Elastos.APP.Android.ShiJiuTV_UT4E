// RUN: %clangxx -O1 %s -o %t && TSAN_OPTIONS="flush_memory_ms=1 memory_limit_mb=1" ASAN_OPTIONS="handle_segv=0 allow_user_segv_handler=1" %run %t 2>&1 | FileCheck %s

// JVM uses SEGV to preempt threads. All threads do a load from a known address
// periodically. When runtime needs to preempt threads, it unmaps the page.
// Threads start triggering SEGV one by one. The signal handler blocks
// threads while runtime does its thing. Then runtime maps the page again
// and resumes the threads.
// Previously this pattern conflicted with stop-the-world machinery,
// because it briefly reset SEGV handler to SIG_DFL.
// As the consequence JVM just silently died.

// This test sets memory flushing rate to maximum, then does series of
// "benign" SEGVs that are handled by signal handler, and ensures that
// the process survive.

#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <sys/mman.h>
#include <string.h>

void *guard;

void handler(int signo, siginfo_t *info, void *uctx) {
  mprotect(guard, 4096, PROT_READ | PROT_WRITE);
}

int main() {
  struct sigaction a, old;
  memset(&a, 0, sizeof(a));
  memset(&old, 0, sizeof(old));
  a.sa_sigaction = handler;
  a.sa_flags = SA_SIGINFO;
  sigaction(SIGSEGV, &a, &old);
  guard = mmap(0, 4096, PROT_NONE, MAP_ANON | MAP_PRIVATE, -1, 0);
  for (int i = 0; i < 1000000; i++) {
    mprotect(guard, 4096, PROT_NONE);
    *(int*)guard = 1;
  }
  sigaction(SIGSEGV, &old, 0);
  fprintf(stderr, "DONE\n");
}

// CHECK: DONE
