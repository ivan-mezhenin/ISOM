
#include "isom.h"
int main() {
    printf("parsing...
");
    Hypergraph* g = parse_hg("P1(a,b)");
    printf("parsed: %p edges=%d
", (void*)g, g ? g->edge_cnt : -1);
    free_hg(g);
    printf("done
");
    return 0;
}
