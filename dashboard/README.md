🔹 Steps to Install & Access the Kubernetes Dashboard on GKE
1. Deploy the Dashboard
```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml```

This creates the dashboard in the kubernetes-dashboard namespace.

2. Create a Service Account & Role Binding
By default, the dashboard has no permissions. Create an admin user:
```
kubectl create serviceaccount dashboard-admin-sa -n kubernetes-dashboard

kubectl create clusterrolebinding dashboard-admin-sa \
  --clusterrole=cluster-admin \
  --serviceaccount=kubernetes-dashboard:dashboard-admin-sa
```

3. Get the Login Token
Fetch the token for the ServiceAccount:
```
kubectl -n kubernetes-dashboard create token dashboard-admin-sa
```
Copy the long JWT token — you’ll need it to log in.
4. Access the Dashboard
Start a proxy to make it accessible:
```
kubectl proxy
```
Then open this URL in your browser:
http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
