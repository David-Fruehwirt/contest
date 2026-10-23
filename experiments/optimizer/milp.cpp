#define main lp_oldmain
#include "lp.cpp"
#undef main
mt19937 gen(43);
double rr(){return double(gen())/gen.max();}
struct Result{long long cost=LLONG_MAX;vector<int>steps;};
vector<Reaction>rs;int K,R;map<int,int>buy;
Result schedule(const vector<double>&x,int target,int need,int trials){
 Result best;
 for(int tr=0;tr<trials;tr++){
 vector<int>cnt(R),inv(K);for(int i=0;i<R;i++)cnt[i]=ceil(x[i]-1e-7);
 vector<int> allowance(K);for(int i=0;i<R;i++){for(auto[m,n]:rs[i].a)allowance[m]+=n*cnt[i];for(auto[m,n]:rs[i].b)allowance[m]-=n*cnt[i];}for(int &v:allowance)v=max(0,v);Result z;z.cost=0;int total=accumulate(cnt.begin(),cnt.end(),0);
 while(total){
  int at=-1;double bv=INF;
  for(int i=0;i<R;i++)if(cnt[i]){
   int cost=0,extra=0;bool ok=true;
   for(auto[m,n]:rs[i].a)if(inv[m]<n){if(prices[m]<0){ok=false;break;}cost+=(n-inv[m])*prices[m];extra+=max(0,n-inv[m]-allowance[m])*prices[m];}
   if(!ok)continue;
   double v=cost+extra*1000+rr()*(tr%4==0?0:tr%4==1?10:tr%4==2?100:1000);
   if(v<bv)bv=v,at=i;
  }
  if(at<0)break;
  cnt[at]--;total--;z.steps.push_back(at);
  for(auto[m,n]:rs[at].a){if(inv[m]<n){z.cost+=(n-inv[m])*prices[m];allowance[m]=max(0,allowance[m]-(n-inv[m]));inv[m]=n;}inv[m]-=n;}
  for(auto[m,n]:rs[at].b)inv[m]+=n;
  if(inv[target]>=need)break;
 }
 if(inv[target]>=need&&z.cost<best.cost)best=z;
 }return best;
}
struct Node {vector<pair<int,int>> hi,lo;double lb;};
int main(int argc,char**argv){
 int M,Q;string s;cin>>M;getline(cin,s);for(int i=0;i<M;i++){getline(cin,s);int p=s.find(" -> ");prices[id(s.substr(p+4))]=stoi(s.substr(0,p));}cin>>R;getline(cin,s);for(int i=0;i<R;i++){getline(cin,s);int p=s.find(" -> ");rs.push_back({side(s.substr(0,p)),side(s.substr(p+4)),s});}cin>>Q;vector<pair<int,int>>qs;for(int i=0,n;i<Q;i++){string m;cin>>n>>m;qs.push_back({id(m),n});}K=ids.size();int V=R+K;vector<vector<double>>A(K,vector<double>(V));vector<double>c(V),b(K);for(int i=0;i<R;i++){for(auto[m,n]:rs[i].a)A[m][i]+=n;for(auto[m,n]:rs[i].b)A[m][i]-=n;}for(int m=0;m<K;m++){if(prices[m]>=0)A[m][R+m]=-1,c[R+m]=-prices[m];else c[R+m]=-10000;}
 int ca=0;for(auto[t,n]:qs){
  fill(b.begin(),b.end(),0);b[t]=-n;vector<double>x;LPSolver lp(A,b,c);double val=-lp.solve(x);Result best=schedule(x,t,n,40);cerr<<"case "<<++ca<<" LB="<<val<<" ceilcost="<<best.cost<<"\n";
  double budget=argc>1?atof(argv[1]):5;auto start=chrono::steady_clock::now();vector<Node>stack(1);int nodes=0,ints=0;
  while(!stack.empty()&&chrono::duration<double>(chrono::steady_clock::now()-start).count()<budget){
   Node node=move(stack.back());stack.pop_back();auto AA=A;auto bb=b;
   for(auto[i,v]:node.hi){vector<double>row(V);row[i]=1;AA.push_back(row);bb.push_back(v);}
   for(auto[i,v]:node.lo){vector<double>row(V);row[i]=-1;AA.push_back(row);bb.push_back(-v);}
   vector<double>xx;LPSolver lpp(AA,bb,c);double obj=-lpp.solve(xx);nodes++;if(obj==INF||obj>=best.cost-1e-7||xx.empty())continue;
   if(nodes%10==0){auto z=schedule(xx,t,n,3);if(z.cost<best.cost)best=z;}
   int branch=-1;double bestfrac=0;for(int i=0;i<R;i++){double f=xx[i]-floor(xx[i]);double frac=min(f,1-f);if(frac>bestfrac+1e-6)branch=i,bestfrac=frac;}
   if(branch<0){auto z=schedule(xx,t,n,40);ints++;if(z.cost<best.cost){best=z;cerr<<"new "<<best.cost<<" nodes="<<nodes<<"\n";}continue;}
   Node ceilnode=node;ceilnode.lo.push_back({branch,(int)ceil(xx[branch])});node.hi.push_back({branch,(int)floor(xx[branch])});
   if(rr()<0.3){stack.push_back(node);stack.push_back(ceilnode);}else {stack.push_back(ceilnode);stack.push_back(node);}
   if(stack.size()>2000)stack.erase(stack.begin());
  }
  cerr<<"final="<<best.cost<<" nodes="<<nodes<<" ints="<<ints<<"\n";
  for(int i:best.steps)cout<<rs[i].s<<"\n";cout<<"\n";
 }
}
