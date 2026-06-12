#include <stdio.h>
#include <stdlib.h>
#include "isom.h"

void test(const char* name, const char* graph1_str, const char* graph2_str) {
    printf("=== %s ===\n", name);
    Hypergraph* graph1 = parse_hypergraph(graph1_str);
    Hypergraph* graph2 = parse_hypergraph(graph2_str);
    
    printf("G1: "); print_hypergraph(graph1);
    printf("G2: "); print_hypergraph(graph2);
    
    Unifier* unifier = check_isomorphism(graph1, graph2);
    
    printf("Result: %s\n", unifier ? "ISOMORPHIC" : "NOT ISOMORPHIC");
    if (unifier) {
        printf("Unifier (one of possible):\n");
        print_unifier(unifier);
        unifier_free(unifier);
    }
    printf("\n");
    
    free_hypergraph(graph1);
    free_hypergraph(graph2);
}

char* read_file(const char* path) {
    FILE* f = fopen(path, "rb");
    if (!f) {
        return NULL;
    }

    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return NULL;
    }

    long len = ftell(f);
    if (len < 0) {
        fclose(f);
        return NULL;
    }

    if (fseek(f, 0, SEEK_SET) != 0) {
        fclose(f);
        return NULL;
    }

    char* buf = (char*)malloc((size_t)len + 1);
    if (!buf) {
        fclose(f);
        return NULL;
    }

    size_t n = fread(buf, 1, (size_t)len, f);
    buf[n] = '\0';

    fclose(f);
    return buf;
}

int main(int argc, char* argv[]) {
    if (argc == 3) {
        char *s1, *s2;
        if (argv[1][0] == '@') {
            s1 = read_file(argv[1] + 1);
            s2 = read_file(argv[2] + 1);
            if (!s1 || !s2) { fprintf(stderr, "File read error\n"); free(s1); free(s2); return 1; }
        } else {
            s1 = strdup(argv[1]);
            s2 = strdup(argv[2]);
        }
        Hypergraph* graph1 = parse_hypergraph(s1);
        Hypergraph* graph2 = parse_hypergraph(s2);
        free(s1); free(s2);
        if (!graph1 || !graph2) {
            fprintf(stderr, "Parse error\n");
            free_hypergraph(graph1); free_hypergraph(graph2);
            return 1;
        }
        Unifier* unifier = check_isomorphism(graph1, graph2);
        printf("%s\n", unifier ? "ISOMORPHIC" : "NOT ISOMORPHIC");
        if (unifier) {
            for (int i = 0; i < unifier->count; i++)
                printf("%s -> %s\n", unifier->subs[i].from, unifier->subs[i].to);
            unifier_free(unifier);
        }
        free_hypergraph(graph1); free_hypergraph(graph2);
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
