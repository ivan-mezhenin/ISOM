#include <stdio.h>
#include <stdlib.h>
#include "isom.h"

void print_uni(Unifier* u) {
    if (!u || u->cnt == 0) { printf("  (none)\n"); return; }
    for (int i = 0; i < u->cnt; i++) {
        printf("  %s -> %s\n", u->subs[i].var, u->subs[i].val);
    }
}

void test(const char* name, const char* g1_str, const char* g2_str) {
    printf("=== %s ===\n", name);
    Hypergraph* G1 = parse_hg(g1_str);
    Hypergraph* G2 = parse_hg(g2_str);
    
    printf("G1: "); print_hg(G1);
    printf("G2: "); print_hg(G2);
    
    Unifier* uni = check_iso(G1, G2);
    
    printf("Result: %s\n", uni ? "ISOMORPHIC" : "NOT ISOMORPHIC");
    if (uni) {
        printf("Unifier (one of possible):\n");
        print_uni(uni);
        free(uni);
    }
    printf("\n");
    
    free_hg(G1);
    free_hg(G2);
}

int main(int argc, char* argv[]) {
    if (argc == 3) {
        // CLI mode: ./isom "g1_str" "g2_str"
        Hypergraph* G1 = parse_hg(argv[1]);
        Hypergraph* G2 = parse_hg(argv[2]);
        if (!G1 || !G2) {
            fprintf(stderr, "Parse error\n");
            free_hg(G1); free_hg(G2);
            return 1;
        }
        Unifier* uni = check_iso(G1, G2);
        printf("%s\n", uni ? "ISOMORPHIC" : "NOT ISOMORPHIC");
        if (uni) {
            for (int i = 0; i < uni->cnt; i++)
                printf("%s -> %s\n", uni->subs[i].var, uni->subs[i].val);
            free(uni);
        }
        free_hg(G1); free_hg(G2);
        return 0;
    }
    
    printf("Hypergraph Isomorphism Checker\n");
    printf("(PDF: Ob izomorfizme gipergrafov otnosheniy)\n\n");
    
    // Test 1: Simple isomorphism
    test("Test 1: Simple Isomorphic", 
         "p3(a1,a2,a3)&p3(a4,a5,a6)", 
         "p3(b1,b2,b3)&p3(b4,b5,b6)");
    
    // Test 2: Not isomorphic (different characteristics)
    test("Test 2: Not Isomorphic", 
         "p3(a1,a2,a3)&p3(a1,a2,a4)", 
         "p3(b1,b2,b3)&p3(b4,b5,b6)");
    
    // Test 3: Overlapping args
    test("Test 3: Overlapping Args", 
         "p3(a,a,b)&p3(a,b,c)", 
         "p3(x,x,y)&p3(x,y,z)");
    
    // Test 4: PDF Example (page 5)
    test("Test 4: PDF Example", 
         "p3(a1,a2,a3)&p3(a4,a5,a6)", 
         "p3(b1,b2,b3)&p3(b4,b5,b6)");
    
    // Test 5: Same graph
    test("Test 5: Same Graph", 
         "p3(a,b,c)&p3(d,e,f)", 
         "p3(a,b,c)&p3(d,e,f)");
    
    // Test 6: Different predicates
    test("Test 6: Different Predicates", 
         "p3(a,b,c)&p3(d,e,f)", 
         "q3(a,b,c)&q3(d,e,f)");
    
    // Test 7: Arity mismatch
    test("Test 7: Arity Mismatch", 
         "p3(a,b,c)", 
         "p2(x,y)");
    
    return 0;
}
