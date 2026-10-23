#include <bits/stdc++.h>
using namespace std;
const double EPS=1e-8, INF=1e100;
struct LPSolver {
 int m,n;vector<int>B,N;vector<vector<double>>D;
 LPSolver(vector<vector<double>> A, vector<double>b,vector<double>c):m(b.size()),n(c.size()),N(n+1),B(m),D(m+2,vector<double>(n+2)){
 for(int i=0;i<m;i++)for(int j=0;j<n;j++)D[i][j]=A[i][j];
 for(int i=0;i<m;i++)B[i]=n+i,D[i][n]=-1,D[i][n+1]=b[i];
 for(int j=0;j<n;j++)N[j]=j,D[m][j]=-c[j];N[n]=-1;D[m+1][n]=1;}
 void pivot(int r,int s){double inv=1/D[r][s];for(int i=0;i<m+2;i++)if(i!=r)for(int j=0;j<n+2;j++)if(j!=s)D[i][j]-=D[r][j]*D[i][s]*inv;for(int j=0;j<n+2;j++)if(j!=s)D[r][j]*=inv;for(int i=0;i<m+2;i++)if(i!=r)D[i][s]*=-inv;D[r][s]=inv;swap(B[r],N[s]);}
 bool simplex(int phase){int x=phase==1?m+1:m;while(1){int s=-1;for(int j=0;j<=n;j++){if(phase==2&&N[j]==-1)continue;if(D[x][j]<-EPS&&(s==-1||N[j]<N[s]))s=j;}if(s==-1)return true;int r=-1;for(int i=0;i<m;i++)if(D[i][s]>EPS){if(r==-1)r=i;else{double a=D[i][n+1]/D[i][s],b=D[r][n+1]/D[r][s];if(a<b-EPS||(abs(a-b)<EPS&&B[i]<B[r]))r=i;}}if(r==-1)return false;pivot(r,s);}}
 double solve(vector<double>&x){int r=0;for(int i=1;i<m;i++)if(D[i][n+1]<D[r][n+1])r=i;if(D[r][n+1]<-EPS){pivot(r,n);if(!simplex(1)||D[m+1][n+1]<-EPS||abs(D[m+1][n+1])>EPS)return -INF;for(int i=0;i<m;i++)if(B[i]==-1){int s=0;for(int j=1;j<=n;j++)if(D[i][j]<D[i][s]-EPS||(abs(D[i][j]-D[i][s])<EPS&&N[j]<N[s]))s=j;pivot(i,s);}}
 if(!simplex(2))return INF;x.assign(n,0);for(int i=0;i<m;i++)if(B[i]<n)x[B[i]]=D[i][n+1];return D[m][n+1];}
};
struct Reaction{vector<pair<int,int>>a,b;string s;};
map<string,int>ids;vector<string>names;vector<int>prices;
int id(string s){if(ids.count(s))return ids[s];int i=ids.size();ids[s]=i;names.push_back(s);prices.push_back(-1);return i;}
vector<pair<int,int>>side(string s){for(char&c:s)if(c==',')c=' ';istringstream ss(s);int n;string m;vector<pair<int,int>>v;while(ss>>n>>m)v.push_back({id(m),n});return v;}
int main(){string s;int M,R,Q;cin>>M;getline(cin,s);for(int i=0;i<M;i++){getline(cin,s);int p=s.find(" -> ");prices[id(s.substr(p+4))]=stoi(s.substr(0,p));}cin>>R;getline(cin,s);vector<Reaction>rs;for(int i=0;i<R;i++){getline(cin,s);int p=s.find(" -> ");rs.push_back({side(s.substr(0,p)),side(s.substr(p+4)),s});}cin>>Q;vector<pair<int,int>>qs;for(int i=0,n;i<Q;i++){string m;cin>>n>>m;qs.push_back({id(m),n});}int K=ids.size(),V=R+K;vector<vector<double>>A(K,vector<double>(V));vector<double>c(V),b(K);for(int i=0;i<R;i++){for(auto[m,n]:rs[i].a)A[m][i]+=n;for(auto[m,n]:rs[i].b)A[m][i]-=n;}for(int m=0;m<K;m++){if(prices[m]>=0)A[m][R+m]=-1,c[R+m]=-prices[m];else c[R+m]=-10000;}
 for(auto[t,n]:qs){fill(b.begin(),b.end(),0);b[t]=-n;vector<double>x;LPSolver lp(A,b,c);double val=lp.solve(x);cerr<<names[t]<<" "<<n<<" lb="<<-val<<" active="<<count_if(x.begin(),x.begin()+R,[](double v){return v>EPS;})<<"\n";for(int i=0;i<V;i++)cout<<setprecision(14)<<x[i]<<" ";cout<<"\n";}
}
