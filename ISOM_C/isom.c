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

void free_hg(Hypergraph* g) { if (g) free(g); }

void print_hg(Hypergraph* g) {
    if (!g) return;
    for (int i = 0; i < g->edge_cnt; i++) {
        Hyperedge* e = &g->edges[i];
        printf("%s(", e->pred);
        for (int j = 0; j < e->arity; j++) {
            printf("%s", e->args[j]);
            if (j < e->arity - 1) printf(",");
        }
        printf(") ");
    }
    printf("\n");
}

// --- Characteristics ---
typedef struct {
    char name[MAX_NAME];
    int vec[MAX_ARGS];
} ArgChar;

typedef struct {
    ArgChar* items;
    int count;
    int arity;
} GraphChar;

GraphChar* calc_char(Hypergraph* g) {
    char uniq[MAX_ARGS][MAX_NAME] = {{0}};
    int ucnt = 0;
    
    for (int i = 0; i < g->edge_cnt; i++)
        for (int j = 0; j < g->edges[i].arity; j++) {
            bool found = false;
            for (int k = 0; k < ucnt; k++)
                if (strcmp(uniq[k], g->edges[i].args[j]) == 0) { found = true; break; }
            if (!found && ucnt < MAX_ARGS) copy_str(uniq[ucnt++], g->edges[i].args[j]);
        }
    
    GraphChar* gc = (GraphChar*)malloc(sizeof(GraphChar));
    gc->count = ucnt;
    gc->arity = g->arity;
    gc->items = (ArgChar*)calloc(ucnt, sizeof(ArgChar));
    
    for (int i = 0; i < ucnt; i++) {
        copy_str(gc->items[i].name, uniq[i]);
        for (int j = 0; j < g->arity; j++) gc->items[i].vec[j] = 0;
        for (int e = 0; e < g->edge_cnt; e++)
            for (int a = 0; a < g->edges[e].arity; a++)
                if (strcmp(g->edges[e].args[a], uniq[i]) == 0)
                    gc->items[i].vec[a]++;
    }
    return gc;
}

void free_char(GraphChar* gc) {
    if (gc) { if (gc->items) free(gc->items); free(gc); }
}

int cmp_argchar(const void* a, const void* b) {
    ArgChar* ac1 = (ArgChar*)a;
    ArgChar* ac2 = (ArgChar*)b;
    for (int i = 0; i < MAX_ARGS; i++) {
        if (ac1->vec[i] < ac2->vec[i]) return -1;
        if (ac1->vec[i] > ac2->vec[i]) return 1;
    }
    return strcmp(ac1->name, ac2->name);
}

void sort_char(GraphChar* gc) {
    qsort(gc->items, gc->count, sizeof(ArgChar), cmp_argchar);
}

bool cmp_chars(GraphChar* c1, GraphChar* c2) {
    if (c1->count != c2->count || c1->arity != c2->arity) return false;
    sort_char(c1);
    sort_char(c2);
    for (int i = 0; i < c1->count; i++)
        for (int j = 0; j < c1->arity; j++)
            if (c1->items[i].vec[j] != c2->items[i].vec[j]) return false;
    return true;
}

// --- Unifiers ---
int get_constants(Hypergraph* g, char res[][MAX_NAME]) {
    int cnt = 0;
    for (int i = 0; i < g->edge_cnt; i++)
        for (int j = 0; j < g->edges[i].arity; j++)
            if (!is_var(g->edges[i].args[j])) {
                bool found = false;
                for (int k = 0; k < cnt; k++)
                    if (strcmp(res[k], g->edges[i].args[j]) == 0) { found = true; break; }
                if (!found && cnt < MAX_ARGS) copy_str(res[cnt++], g->edges[i].args[j]);
            }
    return cnt;
}

int get_variables(Hypergraph* g, char res[][MAX_NAME]) {
    int cnt = 0;
    for (int i = 0; i < g->edge_cnt; i++)
        for (int j = 0; j < g->edges[i].arity; j++)
            if (is_var(g->edges[i].args[j])) {
                bool found = false;
                for (int k = 0; k < cnt; k++)
                    if (strcmp(res[k], g->edges[i].args[j]) == 0) { found = true; break; }
                if (!found && cnt < MAX_ARGS) copy_str(res[cnt++], g->edges[i].args[j]);
            }
    return cnt;
}

// Build template H from G1, returns λ1: const_G1 -> x_i
// Variables in G1 are kept as-is (they become part of H)
Hypergraph* build_template(Hypergraph* g1, Unifier* lambda1) {
    Hypergraph* H = (Hypergraph*)calloc(1, sizeof(Hypergraph));
    H->edge_cnt = g1->edge_cnt;
    H->arity = g1->arity;
    lambda1->cnt = 0;
    
    // Collect constants and assign them new variable names
    char consts[MAX_ARGS][MAX_NAME] = {{0}};
    int ccnt = 0;
    
    for (int i = 0; i < g1->edge_cnt; i++) {
        for (int j = 0; j < g1->edges[i].arity; j++) {
            char* arg = g1->edges[i].args[j];
            if (!is_var(arg)) {  // It's a constant
                bool found = false;
                for (int k = 0; k < ccnt; k++) {
                    if (strcmp(consts[k], arg) == 0) { found = true; break; }
                }
                if (!found && ccnt < MAX_ARGS) {
                    copy_str(consts[ccnt], arg);
                    // Create mapping: constant -> new variable x_i
                    char vn[MAX_NAME];
                    sprintf(vn, "x%d", ccnt + 1);
                    copy_str(lambda1->subs[lambda1->cnt].var, consts[ccnt]);
                    copy_str(lambda1->subs[lambda1->cnt].val, vn);
                    lambda1->cnt++;
                    ccnt++;
                }
            }
        }
    }
    
    // Build H: replace constants with their x_i, keep variables as-is
    for (int i = 0; i < g1->edge_cnt; i++) {
        copy_str(H->edges[i].pred, g1->edges[i].pred);
        H->edges[i].arity = g1->edges[i].arity;
        for (int j = 0; j < g1->edges[i].arity; j++) {
            char* arg = g1->edges[i].args[j];
            if (is_var(arg)) {
                // Variable in G1 stays as-is in H
                copy_str(H->edges[i].args[j], arg);
            } else {
                // Constant: replace with its variable
                for (int k = 0; k < lambda1->cnt; k++) {
                    if (strcmp(arg, lambda1->subs[k].var) == 0) {
                        copy_str(H->edges[i].args[j], lambda1->subs[k].val);
                        break;
                    }
                }
            }
        }
    }
    return H;
}

Hypergraph* apply_uni(Hypergraph* g, Unifier* u) {
    Hypergraph* res = (Hypergraph*)calloc(1, sizeof(Hypergraph));
    res->edge_cnt = g->edge_cnt;
    res->arity = g->arity;
    
    for (int i = 0; i < g->edge_cnt; i++) {
        copy_str(res->edges[i].pred, g->edges[i].pred);
        res->edges[i].arity = g->edges[i].arity;
        for (int j = 0; j < g->edges[i].arity; j++) {
            bool found = false;
            for (int k = 0; k < u->cnt; k++)
                if (strcmp(g->edges[i].args[j], u->subs[k].var) == 0) {
                    copy_str(res->edges[i].args[j], u->subs[k].val);
                    found = true;
                    break;
                }
            if (!found) copy_str(res->edges[i].args[j], g->edges[i].args[j]);
        }
    }
    return res;
}

// Compose u1 and u2: apply u2 to values of u1
Unifier* compose(Unifier* u1, Unifier* u2) {
    Unifier* res = (Unifier*)calloc(1, sizeof(Unifier));
    for (int i = 0; i < u1->cnt && res->cnt < MAX_ARGS * 2; i++) {
        copy_str(res->subs[res->cnt].var, u1->subs[i].var);
        char fv[MAX_NAME] = {0};
        copy_str(fv, u1->subs[i].val);
        for (int j = 0; j < u2->cnt; j++)
            if (strcmp(fv, u2->subs[j].var) == 0) {
                copy_str(fv, u2->subs[j].val);
                break;
            }
        copy_str(res->subs[res->cnt].val, fv);
        res->cnt++;
    }
    return res;
}

// --- Isomorphism checks ---
bool is_literal_iso(char a1[][MAX_NAME], char a2[][MAX_NAME], int arity) {
    int i1 = 0, i2 = 0;
    
    for (int i = 0; i < arity; i++) {
        int id1 = -1;
        for (int j = 0; j < i1; j++) if (strcmp(a1[i], a1[j]) == 0) { id1 = j; break; }
        if (id1 == -1) { id1 = i1; i1++; }
        
        int id2 = -1;
        for (int j = 0; j < i2; j++) if (strcmp(a2[i], a2[j]) == 0) { id2 = j; break; }
        if (id2 == -1) { id2 = i2; i2++; }
        
        if (id1 != id2) return false;
    }
    return true;
}

bool edge_is_iso(Hyperedge* e1, Hyperedge* e2) {
    if (e1->arity != e2->arity) return false;
    if (strcmp(e1->pred, e2->pred) != 0) return false;
    return is_literal_iso(e1->args, e2->args, e1->arity);
}

bool hg_is_iso(Hypergraph* g1, Hypergraph* g2) {
    if (g1->edge_cnt != g2->edge_cnt) return false;
    bool used[MAX_EDGES] = {false};
    for (int i = 0; i < g1->edge_cnt; i++) {
        bool found = false;
        for (int j = 0; j < g2->edge_cnt; j++) {
            if (!used[j] && edge_is_iso(&g1->edges[i], &g2->edges[j])) {
                used[j] = true;
                found = true;
                break;
            }
        }
        if (!found) return false;
    }
    return true;
}

// --- Find λ2 (stop at first) ---
bool search_lambda2(Hypergraph* H, Hypergraph* G2,
                    Unifier* cur, int depth,
                    char vars[][MAX_NAME], int var_cnt,
                    char consts[][MAX_NAME], int const_cnt,
                    bool used_consts[]) {
    if (depth == var_cnt) {
        Hypergraph* Hp = apply_uni(H, cur);
        if (Hp && hg_is_iso(Hp, G2)) {
            // Found! Copy result to cur (it's already there)
            if (Hp) free_hg(Hp);
            return true;
        }
        if (Hp) free_hg(Hp);
        return false;
    }
    
    char var[MAX_NAME];
    copy_str(var, vars[depth]);
    
    for (int i = 0; i < const_cnt; i++) {
        if (used_consts[i]) continue;
        
        copy_str(cur->subs[cur->cnt].var, var);
        copy_str(cur->subs[cur->cnt].val, consts[i]);
        cur->cnt++;
        used_consts[i] = true;
        
        if (search_lambda2(H, G2, cur, depth + 1, vars, var_cnt, consts, const_cnt, used_consts)) {
            return true;  // Stop at first found
        }
        
        cur->cnt--;
        used_consts[i] = false;
    }
    return false;
}

// Get ALL unique arguments (variables and constants) from a hypergraph
int get_all_args(Hypergraph* g, char res[][MAX_NAME]) {
    int cnt = 0;
    for (int i = 0; i < g->edge_cnt; i++)
        for (int j = 0; j < g->edges[i].arity; j++) {
            bool found = false;
            for (int k = 0; k < cnt; k++)
                if (strcmp(res[k], g->edges[i].args[j]) == 0) { found = true; break; }
            if (!found && cnt < MAX_ARGS) copy_str(res[cnt++], g->edges[i].args[j]);
        }
    return cnt;
}

// --- Main function: returns ONE unifier or NULL ---
Unifier* check_iso(Hypergraph* g1, Hypergraph* g2) {
    // 1. Check characteristics (necessary condition from PDF)
    GraphChar* c1 = calc_char(g1);
    GraphChar* c2 = calc_char(g2);
    
    if (!cmp_chars(c1, c2)) {
        free_char(c1); free_char(c2);
        return NULL;
    }
    
    // 2. Build template H and λ1: constants of G1 -> variables x_i
    Unifier lambda1;
    lambda1.cnt = 0;
    Hypergraph* H = build_template(g1, &lambda1);
    
    // 3. Get variables in H and ALL arguments in G2 (both vars and constants)
    char vars[MAX_ARGS][MAX_NAME] = {{0}};
    int var_cnt = get_variables(H, vars);
    
    char all_args[MAX_ARGS][MAX_NAME] = {{0}};
    int all_cnt = get_all_args(g2, all_args);
    
    // 4. Search for λ2 (stop at first)
    Unifier lambda2;
    lambda2.cnt = 0;
    bool used_args[MAX_ARGS] = {false};
    
    if (!search_lambda2(H, g2, &lambda2, 0, vars, var_cnt, all_args, all_cnt, used_args)) {
        // No isomorphism found
        free_hg(H);
        free_char(c1);
        free_char(c2);
        return NULL;
    }
    
    // 5. Compose λ = λ1 ∘ λ2
    Unifier* result = compose(&lambda1, &lambda2);
    
    // Cleanup
    free_hg(H);
    free_char(c1);
    free_char(c2);
    
    return result;
}
