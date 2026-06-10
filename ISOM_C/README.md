# Hypergraph Isomorphism Checker

Implementation of hypergraph isomorphism algorithm from PDF:  
**"Ob izomorfizme gipergrafov otnosheniy"**

## Algorithm Description (PDF Section 3.1)

1. **Calculate characteristics** of arguments (Definition 2, 3)
   - For each argument, build a vector of occurrences per position
   - Example: `χ(a1) = (1, 0, 0)` means `a1` appears once in position 1

2. **Build template H** from G1
   - Replace constants in G1 with new variables `x1, x2, ...`
   - Get unifier λ1: `constant → x_i`

3. **Find λ2** using backtracking
   - Map variables of H to constants of G2
   - Check consistency at each step

4. **Compose** λ = λ1 ∘ λ2
   - Final unifier maps constants of G1 to constants of G2

## Building

```bash
make
# or manually:
gcc -o isom main.c isom.c
```

## Running

```bash
./isom
```

## Usage in Code

```c
#include "isom.h"

Hypergraph* G1 = parse_hg("p3(a1,a2,a3)&p3(a4,a5,a6)");
Hypergraph* G2 = parse_hg("p3(b1,b2,b3)&p3(b4,b5,b6)");

Unifier* uni = check_iso(G1, G2);
if (uni) {
    printf("ISOMORPHIC\n");
    // uni contains the mapping
    for (int i = 0; i < uni->cnt; i++) {
        printf("%s -> %s\n", uni->subs[i].var, uni->subs[i].val);
    }
    free(uni);
} else {
    printf("NOT ISOMORPHIC\n");
}

free_hg(G1);
free_hg(G2);
```

## Test Cases

| Test | G1 | G2 | Result |
|------|----|----|--------|
| 1 | p3(a1,a2,a3) p3(a4,a5,a6) | p3(b1,b2,b3) p3(b4,b5,b6) | ISOMORPHIC |
| 2 | p3(a1,a2,a3) p3(a1,a2,a4) | p3(b1,b2,b3) p3(b4,b5,b6) | NOT ISOMORPHIC |
| 3 | p3(a,a,b) p3(a,b,c) | p3(x,x,y) p3(x,y,z) | ISOMORPHIC |
| 4 | p3(a1,a2,a3) p3(a4,a5,a6) | p3(b1,b2,b3) p3(b4,b5,b6) | ISOMORPHIC |
| 5 | p3(a,b,c) p3(d,e,f) | p3(a,b,c) p3(d,e,f) | ISOMORPHIC |
| 6 | p3(a,b,c) p3(d,e,f) | q3(a,b,c) q3(d,e,f) | NOT ISOMORPHIC |
| 7 | p3(a,b,c) | p2(x,y) | NOT ISOMORPHIC |

## Files

- `isom.h` - Header file with structures and function declarations
- `isom.c` - Algorithm implementation
- `main.c` - Test cases
- `Makefile` - Build configuration

## License

Educational use.
