#include "isom.h"
#include <ctype.h>

void copy_str(char* d, const char* s) {
    strncpy(d, s, MAX_NAME - 1);
    d[MAX_NAME - 1] = '\0';
}

bool is_var(const char* s) {
    return s && s[0] == 'x';
}

// --- Parsing ---
Hypergraph* parse_hg(const char* str) {
    Hypergraph* g = (Hypergraph*)calloc(1, sizeof(Hypergraph));
    const char* p = str;
    
    while (*p && g->edge_cnt < MAX_EDGES) {
        while (*p == ' ') p++;
        const char* pred_start = p;
        while (*p && *p != '(') p++;
        if (!*p) break;
        
        Hyperedge* e = &g->edges[g->edge_cnt];
        int plen = p - pred_start;
        if (plen >= MAX_NAME) plen = MAX_NAME - 1;
        strncpy(e->pred, pred_start, plen);
        e->pred[plen] = '\0';
        
        p++;
        const char* args_start = p;
        while (*p && *p != ')') p++;
        if (*p != ')') { free(g); return NULL; }
        
        char args_str[1024] = {0};
        strncpy(args_str, args_start, p - args_start);
        
        e->arity = 0;
        char* tok = strtok(args_str, ",");
        while (tok && e->arity < MAX_ARGS) {
            copy_str(e->args[e->arity], tok);
            e->arity++;
            tok = strtok(NULL, ",");
        }
        
        if (g->edge_cnt == 0) g->arity = e->arity;
        g->edge_cnt++;
        p++;
        
        while (*p == ' ') p++;
        if (*p == '&') p++;
        else break;
    }
    return g;
}

