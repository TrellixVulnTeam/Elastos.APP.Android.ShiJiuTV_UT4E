// RUN: %clangxx_cfi -o %t %s
// RUN: not --crash %t 2>&1 | FileCheck --check-prefix=CFI %s

// RUN: %clangxx_cfi -DB32 -o %t %s
// RUN: not --crash %t 2>&1 | FileCheck --check-prefix=CFI %s

// RUN: %clangxx_cfi -DB64 -o %t %s
// RUN: not --crash %t 2>&1 | FileCheck --check-prefix=CFI %s

// RUN: %clangxx_cfi -DBM -o %t %s
// RUN: not --crash %t 2>&1 | FileCheck --check-prefix=CFI %s

// RUN: %clangxx -o %t %s
// RUN: %t 2>&1 | FileCheck --check-prefix=NCFI %s

// RUN: %clangxx_cfi_diag -o %t %s
// RUN: %t 2>&1 | FileCheck --check-prefix=CFI-DIAG %s

// Tests that the CFI enforcement also applies to virtual destructor calls made
// via 'delete'.

// REQUIRES: cxxabi

#include <stdio.h>
#include "utils.h"

struct A {
  virtual ~A();
};

A::~A() {}

struct B {
  virtual ~B();
};

B::~B() {}

int main() {
#ifdef B32
  break_optimization(new Deriver<B, 0>);
#endif

#ifdef B64
  break_optimization(new Deriver<B, 0>);
  break_optimization(new Deriver<B, 1>);
#endif

#ifdef BM
  break_optimization(new Deriver<B, 0>);
  break_optimization(new Deriver<B, 1>);
  break_optimization(new Deriver<B, 2>);
#endif

  A *a = new A;
  break_optimization(a);

  // CFI: 1
  // NCFI: 1
  fprintf(stderr, "1\n");

  // CFI-DIAG: runtime error: control flow integrity check for type 'B' failed during virtual call
  // CFI-DIAG-NEXT: note: vtable is of type 'A'
  delete (B *)a; // UB here

  // CFI-NOT: 2
  // NCFI: 2
  fprintf(stderr, "2\n");
}
