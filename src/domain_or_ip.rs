#[derive(Debug, Clone, Eq, PartialEq, serde::Deserialize, serde::Serialize)]
pub enum DomainOrIp
{
    Domain(String),
    Ip(std::net::IpAddr),
}


impl From<DomainOrIp> for String // DomainOrIp -> String
{
    fn from(value: DomainOrIp) -> Self
    {
        match value
        {
            DomainOrIp::Domain(domain) => domain,
            DomainOrIp::Ip(ip) => ip.to_string(),
        }
    }
}
